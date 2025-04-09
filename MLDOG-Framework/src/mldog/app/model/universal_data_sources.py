import socket
import time
import os
import numpy as np

from struct import *

from .data_source import MeasurementConfiguration, ChannelConfiguration, DataSource



class UDPDataSource(DataSource):
    """
    The UDP data source provides access to live measurement data received via UDP.
    """
    
    def __init__(self, port=4245, capturama_ip='localhost', capturama_port=4242):
        """
        Construct a new UDP data source.
        """
        
        DataSource.__init__(self, 'UDP Data Source')
        # super().__init__('UDP Data Source')

        self.port = port
        self.socket = None
        self.seq_no = 0

        self.capturama_addr = (capturama_ip, capturama_port)


    def setup(self):
        if self.socket is None:
            # captureProcess = subprocess.Popen(['capturama', '--controller', 'udp', '--provider', 'drillmcc', '--handler', 'udp'])

            # time.sleep(2)

            # create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1)
            self.socket.bind(("", self.port))
            self.socket.sendto('startmsg'.encode('utf-8'), self.capturama_addr)


    def shutdown(self):
        if self.socket is not None:
            # self.socket.sendto('exit'.encode('utf-8'), self.capturamaAddr)

            # discard socket
            self.socket.close()
            self.socket = None
            self.seq_no = 0

            self.data_queue = None


    def startMeasurement(self, data_queue):
        super().startMeasurement(data_queue)

        # self.socket.sendto('startmsg'.encode('utf-8'), self.capturama_addr)
        return True


    def stopMeasurement(self):
        super().stopMeasurement()
        # self.socket.sendto('stopmsg'.encode('utf-8'), self.capturama_addr)


    def receiveLoop(self):
        """
        The receiveLoop-function run by the data receive thread.
        """

        while self.socket is not None:
            try:
                msg, _ = self.socket.recvfrom(4244)
            except(socket.timeout):
                continue
            except Exception as e:
                print(e)
                return
            
            # process received message
            
            # packet structure:
            # bytes: type, description
            # 0-3: uint32 sequence number
            # 4-7: packet type
            # 8-n: payload
            n_bytes = len(msg)

            # unpack sequence number and packet type
            seq_no, pkt_type = unpack_from('<LL', msg, 0)

            # print(f'{seq_no}-{pkt_type}: ', end='')

            if (seq_no == 0 and pkt_type == 0):
                # meta packet with new channel information
                print('Recieved meta data information.')
                
                self.seq_no = 0
                self.parseMetaInformation(msg)
                # self.publish(self.mconfig)
            elif (self.mconfig is None or seq_no < self.seq_no + 1):
                # discard lost packets
                print('discarded!')
            else:
                # update sequence number
                self.seq_no = seq_no

                if (pkt_type == 1):
                    # sensor data packet
                    sensor_data = self.parseSensorData(msg)
                    self.publish(sensor_data)
                elif (pkt_type == 2):
                    # measurement ended packet
                    print('Recieved measurement end notification.')
                    
                    # reset sequence number and channel configuration
                    self.seq_no = 0
                    self.mconfig = None
                    self.data_queue = None
                else:
                    # unknown/unexpected packet type
                    print(f'Recieved unknown/unexpected packet type: {pkt_type}')


    def parseMetaInformation(self, data):
        """
        Parse measurement configuration data.
        """
        
        n_bytes = len(data)

        # unpack sequence number and packet type
        offset = 8
        frequency = unpack_from('<L', data, offset)[0]
        offset += 4

        # unpack channel information
        channels = []
        channel_str = data[offset:].decode('ascii')
        for cidx, cname in enumerate(channel_str.split(',')):
            channels.append(ChannelConfiguration(cidx, cname))

        self.mconfig = MeasurementConfiguration(frequency, channels)


    def parseSensorData(self, data):
        """
        Parse sensor data.
        """

        n_channels = len(self.mconfig.channels)
        n_bytes = len(data)
        n_values = int((n_bytes - 8) / 4)  # n float values subtracting the header size
        n_samples = int(n_values / n_channels)
        unpack_format = '<' + 'f' * n_channels

        sensor_data = []

        for idx in range(0, n_samples):
            sample = unpack_from(unpack_format, data, 8 + idx * n_channels * 4)
            sensor_data.append(sample)

        sensor_data = np.array(sensor_data)

        # print(f'Seq: {self.seq_no}: {len(sensor_data)}')
        
        return sensor_data



class LogDataSource(DataSource):
    """
    The log data source provides access to recorded measurement series.
    """

    def __init__(self, path:str = '../data', block_size:int = 480, frequency:int = 96000):
        """
        Construct a new log data source instance.
        """

        DataSource.__init__(self, 'Log Data Source')
        # super().__init__('Log Data Source')

        self.path = path
        self.data_files = None

        self.file_idx = 0
        self.file_path = None

        self.block_size = block_size
        self.frequency = frequency
    

    def setup(self):
        self.file_idx = 0

        # read file names from specified directory
        dir_list = os.listdir(self.path)
        # print(dir_list)

        # filter measurement files
        self.data_files = list(filter(lambda fname: fname.endswith('.csv'), dir_list))
        print(f'-> Log Files: {self.data_files}')

        return len(self.data_files) > 0
    

    def shutdown(self):
        super().shutdown()

        self.data_files = None
        self.file_path = None


    def startMeasurement(self, data_queue):
        # forward call to base class
        super().startMeasurement(data_queue)

        # proceed to next file
        self.file_path = os.path.join(self.path, self.data_files[self.file_idx])
        self.file_idx = (self.file_idx + 1) % len(self.data_files)

        print('Loading file:', self.file_path)


    def stopMeasurement(self):
        # forward call to base class
        super().stopMeasurement()

        # clear active file
        self.file_path = None
    

    def receiveLoop(self):
        while self.data_files is not None:
            if self.file_path is not None:
                # try to extract the measurement frequency from file name
                frequency = self.file_path.split('_')[-1]
                if len(frequency) > 1 and frequency.endswith('Hz.csv'):
                    frequency = float(frequency.removesuffix('Hz.csv'))
                else:
                    frequency = self.frequency

                with open(self.file_path) as f:
                    row_idx = 0

                    for i, line in enumerate(f):
                        if self.file_path is None:
                            # break processing if file_path got reset
                            break

                        # split next line
                        row_values = line.strip().split(',')

                        if i == 0:
                            # read channel config
                            channels = []
                            for cidx, cname in enumerate(row_values):
                                channels.append(ChannelConfiguration(cidx, cname))
                            self.mconfig = MeasurementConfiguration(frequency, channels)

                            # setup sensor data array shape according to channel config
                            sensor_data: np.ndarray = np.zeros((self.block_size, len(row_values)))

                            # skip further processing for first line
                            continue

                        # set sensor data at current row index
                        sensor_data[row_idx, :] = np.array(row_values)

                        # increment row index
                        row_idx += 1

                        # publish sensor data if chunk is complete
                        if row_idx == self.block_size:
                            self.publish(sensor_data.copy())
                            row_idx = 0
                            time.sleep(self.block_size / self.mconfig.frequency)
                    
                    # publish remaining sensor data chunk
                    if row_idx > 0:
                        self.publish(sensor_data[:row_idx, :].copy())
                    
                    # check for 
                    if self.file_path is not None:
                        print('Reached end of file -> stopping measurement.')

                        # trigger measurement stop
                        # FIXME: Evil call! Not thread save due to event dispatching!
                        self.stopMeasurement()
            else:
                time.sleep(.1)



class DummyDataSource(DataSource):
    """
    The dummy data source generates random measurement series (for testing).
    """

    def __init__(self, n_channels=3, block_size=10, frequency=1000):
        DataSource.__init__(self, 'Dummy Data Source')
        # super().__init__('Dummy Data Source')

        self.last = np.random.rand(block_size, n_channels)
        self.eps = 0.01
        self.frequency = frequency

        self.stop_receiving = False

        self.mconfig = MeasurementConfiguration(frequency, [ChannelConfiguration(i, 'Channel' + str(i)) for i in range(n_channels)])
    

    def setup(self):
        return True
    

    def shutdown(self):
        super().shutdown()

        self.stop_receiving = True


    def receiveLoop(self):
        self.stop_receiving = False

        while not self.stop_receiving:
            time.sleep(self.last.shape[0] / self.frequency)
            re = np.random.randn(*self.last.shape) * self.eps
            self.last = self.last[-1, :] + np.cumsum(re, axis=0)

            self.publish(self.last)
