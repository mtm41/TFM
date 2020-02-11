class Event:
    def __init__(self, provider, system, userdate):
        self.provider = provider
        self.system = system
        self.userdate = userdate
        self.timecreated = ""

    def checkEventTime(self, date):
        creationDateStr = self.timecreated.items()[0][1]
        creationDate = creationDateStr.split(":")
        creationYear = creationDate[0].split("-")[0]
        creationMonth = creationDate[0].split("-")[1]
        creationDay = creationDate[0].split("-")[2].split("T")[0]
        creationHour = creationDate[0].split("-")[2].split("T")[1]
        creationMinute = creationDate[1]
        if str(date.year) == creationYear and date.month == int(creationMonth) \
                and date.day == int(creationDay) and date.hour == int(creationHour) \
                and int(date.minute - int(creationMinute)) <= 5:
            print('ALERT')
        print(creationDateStr)
        return True