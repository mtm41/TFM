from Event import Event


class SystemUpdateEvent(Event):
    def __init__(self, id, timeCreated, data, sourceName):
        super().__init__(id, timeCreated, data)
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
        if self.data and self.provider == 19:
            if date.year == self.timecreated.year and date.month == self.timecreated.month \
                    and date.day == self.timecreated.day and date.hour+1 == self.timecreated.hour \
                    and int(date.minute - self.timecreated.minute) <= 5:
                print('Hay una actualización del sistema')
                print(self.data)
                good = True

        return good
