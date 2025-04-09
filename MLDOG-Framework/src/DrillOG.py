from mldog.app.context import DefaultDrillContext
from mldog.app.ui.ui import MLDOGUI



if __name__ == '__main__':
    context = DefaultDrillContext()
    ui = MLDOGUI(context)
    ui.run()

