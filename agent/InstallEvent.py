from Event import Event


class InstallEvent(Event):
    def __init__(self, provider, timeCreated, data, sourceName):
        super().__init__(provider, timeCreated, data)
        self.timecreated = timeCreated
        self.data = data
        self.sourceName = sourceName

    def checkEvent(self, date):
        good = False

        if (self.data and "Installation" in self.data) or self.sourceName == "Microsoft-Windows-RestartManager":
            if date.year == self.timecreated.year and date.month == self.timecreated.month \
                    and date.day == self.timecreated.day and date.hour+1 == self.timecreated.hour \
                    and int(date.minute - self.timecreated.minute) <= 5:
                print('ALERT')
                good = True

        return good
