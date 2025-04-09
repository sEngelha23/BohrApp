class EventDispatcher:
    """
    Simple class for dispatching events.
    """

    def __init__(self):
        """
        Create a new event dispatcher instance.
        """

        self._listeners = {}
    
    def addListener(self, event, command):
        """
        Add the given listener for the specified event.
        """
        
        # ensure event listener list exists
        if event not in self._listeners:
            self._listeners[event] = []
        
        self._listeners[event].append(command)
    
    def removeListener(self, event, command):
        """
        Remove the given listener for the specified event.
        """
        
        if event in self._listeners:
            self._listeners[event].remove(command)
    
    def _dispatchEvent(self, event, **kwargs):
        """
        Notify listener instances.
        """
        
        if event in self._listeners:
            listeners = self._listeners[event]
            for l in listeners:
                l(**kwargs)
