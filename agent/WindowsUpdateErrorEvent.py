from Event import Event


class WindowsUpdateErrorEvent(Event):
    def __init__(self, provider, system, userdata):
        super().__init__(provider, system, userdata)
        self.level = 2
        self.opcode = 12
        self.timecreated = system[7]

    def checkEvent(self, date, lastCheck):
        good = False
        if self.checkEventTime(date, lastCheck):
            if self.system[1].text == "31":
                good = True
            elif self.system[1].text == "25":
                good = True
        return good
