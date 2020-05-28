import math


class Event:
    def __init__(self, provider, system, userdate):
        self.provider = provider
        self.system = system
        self.userdate = userdate
        self.timecreated = ""

    def getSourceName(self):
        return None

    def checkEventTime(self, date, lastCheck):
        if lastCheck is not None:
            interval = math.ceil((date - lastCheck).total_seconds() / 60)
        else:
            interval = 3
        good = False
        creationDateStr = self.timecreated.items()[0][1]
        creationDate = creationDateStr.split(":")
        creationYear = creationDate[0].split("-")[0]
        creationMonth = creationDate[0].split("-")[1]
        creationDay = creationDate[0].split("-")[2].split("T")[0]
        creationHour = creationDate[0].split("-")[2].split("T")[1]
        creationMinute = creationDate[1]
        if str(date.year) == creationYear and date.month == int(creationMonth) \
                and date.day == int(creationDay) and date.hour == int(creationHour) \
                and int(date.minute - int(creationMinute)) <= interval:
            print('ALERT')
            good = True
        return good
