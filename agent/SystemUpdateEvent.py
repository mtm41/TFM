import math

from Event import Event


class SystemUpdateEvent(Event):
    def __init__(self, sid, provider, timeCreated, data, sourceName, id):
        super().__init__(provider, timeCreated, data)
        self.id = id
        self.timecreated = timeCreated
        if data:
            self.data = data[0]
        else:
            self.data = ""
        self.sourceName = sourceName

    def getSourceName(self):
        return self.sourceName

    def getTimeCreated(self):
        return self.timecreated

    def checkEvent(self, date, suspiciousEvents, importantsEvents, lastCheck):
        if lastCheck is not None:
            interval = math.ceil((date - lastCheck).total_seconds() / 60)
        else:
            interval = 3
        good = False
        if self.data and self.id == 19:
            if date.year == self.timecreated.year and date.month == self.timecreated.month \
                    and date.day == self.timecreated.day and date.hour+1 == self.timecreated.hour \
                    and int(date.minute - self.timecreated.minute) <= interval:
                good = True

        return good
