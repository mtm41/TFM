from Event import Event


class InstallEvent(Event):
    def __init__(self, provider, timeCreated, data, sourceName, eventID=0):
        super().__init__(provider, timeCreated, data)
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

    def checkEvent(self, date):
        good = False

        if self.data and "Installation" in self.data:
            if date.year == self.timecreated.year and date.month == self.timecreated.month \
                    and date.day == self.timecreated.day and date.hour+1 == self.timecreated.hour \
                    and int(date.minute - self.timecreated.minute) <= 5:
                print('Hay una instalación hecha por un MsiInstaller')
                good = True

        return good
