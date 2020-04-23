from Event import Event
from InstallEvent import InstallEvent


class SelfInstallWarnEvent(Event):
    def __init__(self, provider, timeCreated, data="", sourceName="", eventID=0):
        super().__init__(provider, timeCreated, None)
        self.timecreated = timeCreated
        self.eventID = eventID
        self.sourceName = sourceName

    def getSourceName(self):
        return self.sourceName

    def checkDuplicatedSelfInstall(self, importantEvents):
        duplicated = False
        for event in importantEvents:
            if event.getSourceName() == "Microsoft-Windows-User Profiles Service":
                duplicated = True
                break

        return duplicated

    def checkSuspiciousInstall(self, suspiciousEvents):
        installer = False
        for event in suspiciousEvents:
            if event.getSourceName() == "MsiInstaller":
                installer = True
                break

        return installer


    def checkEvent(self, date, suspiciousEvents, importantEvents):
        good = False
        if not self.checkDuplicatedSelfInstall(importantEvents) and not self.checkSuspiciousInstall(suspiciousEvents):
            if date.year == self.timecreated.year and date.month == self.timecreated.month \
                    and date.day == self.timecreated.day and date.hour+2 == self.timecreated.hour \
                    and abs(int(date.minute - self.timecreated.minute)) <= 5:
                good = True
                print(self.timecreated)
                print('INSTALACIOND E EDITOR NO CONOCIDO')
        return good