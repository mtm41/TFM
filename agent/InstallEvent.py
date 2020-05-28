import math

from Event import Event


class InstallEvent(Event):
    def __init__(self, sid, provider, timeCreated, data, sourceName, eventID=0):
        super().__init__(provider, timeCreated, data)
        self.timecreated = timeCreated
        if data:
            self.data = data[0]
        else:
            self.data = ""
        self.sourceName = sourceName
        self.userID = sid

    def getSourceName(self):
        return self.sourceName

    def getTimeCreated(self):
        return self.timecreated

    def checkEvent(self, date, suspiciousEvents, importantsEvents, lastCheck):
        good = False
        if lastCheck is not None:
            interval = math.ceil((date - lastCheck).total_seconds() / 60)
        else:
            interval = 3
        if self.data and "Installation" in self.data:
            if date.year == self.timecreated.year and date.month == self.timecreated.month \
                    and date.day == self.timecreated.day and date.hour+2 == self.timecreated.hour \
                    and abs(int(date.minute - self.timecreated.minute)) <= interval:
                good = True

        return good
