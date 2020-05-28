import math

from Event import Event
from InstallEvent import InstallEvent


class SelfInstallEvent(Event):
    def __init__(self, provider, timeCreated, data="", sourceName="", eventID=0):
        super().__init__(provider, timeCreated, None)
        self.timecreated = timeCreated
        self.eventID = eventID
        self.sourceName = sourceName

    def getSourceName(self):
        return self.sourceName

    """
        It will return TRUE if an event has happened in last 5 minutes and his type is RestartManager, but also
        there is one more event of type MsiInstaller at least. These reasons could prove that a self installation
        (known editor) has happened in the system.
    """
    def checkEvent(self, date, suspiciousEvents, importantsEvents, lastCheck):
        good = False

        if self.checkDate(date, self.timecreated, lastCheck):
            if self.eventID == 10001:
                good = True
                print('POSIBLE INSTALACION, POR UN INSTALADOR PROPIO')
                print(suspiciousEvents)
                for event in suspiciousEvents:
                    if self.checkDate(date, event.getTimeCreated()) and event.getSourceName() == "MsiInstaller":
                        print('Hay un restart manager, pero posiblemente debido a un MsiInstaller')
                        good = False
                        break

        return good

    def checkDate(self, date, timeCreated, lastCheck):
        if lastCheck is not None:
            interval = math.ceil((date - lastCheck).total_seconds() / 60)
        else:
            interval = 3
        good = False
        if date.year == timeCreated.year and date.month == timeCreated.month \
                and date.day == timeCreated.day and date.hour+2 == timeCreated.hour \
                and abs(int(date.minute - timeCreated.minute)) <= interval:
            good = True
            print(timeCreated)
        return good
