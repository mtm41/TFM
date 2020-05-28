from Event import Event


class ExtDevEvent(Event):
    def __init__(self, provider, system, userdata):
        super().__init__(provider, system, userdata)
        self.level = 5
        self.opcode = 1

    def checkEvent(self, date, lastCheck):
        good = False
        if int(self.system[3].text) == self.level and int(self.system[5].text) == self.opcode:
            self.timecreated = self.system[7]
            if self.checkEventTime(date, lastCheck):
                good = True

        return good
