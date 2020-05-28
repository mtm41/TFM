from PySide2.QtCore import QRunnable, QThreadPool

from ActionResponse import ActionResponse


class ProcessRunnable(QRunnable):
    def __init__(self, args):
        QRunnable.__init__(self)
        self.t = ActionResponse().show_alert_window
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)