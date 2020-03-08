from Event import Event
from InstallEvent import InstallEvent


class SelfInstallWarnEvent(Event):
    def __init__(self, provider, timeCreated, eventID, sourceName):
        super().__init__(provider, timeCreated, None)
        self.timecreated = timeCreated
        self.eventID = eventID
        self.sourceName = sourceName

    def getSourceName(self):
        return self.sourceName

    def checkEvent(self, date):
        good = False

        if date.year == self.timecreated.year and date.month == self.timecreated.month \
                and date.day == self.timecreated.day and date.hour + 1 == self.timecreated.hour \
                and int(date.minute - self.timecreated.minute) <= 5:
            good = True
        return good