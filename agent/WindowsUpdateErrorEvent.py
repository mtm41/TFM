from Event import Event


class WindowsUpdateErrorEvent(Event):
    def __init__(self, provider, system, userdata):
        super().__init__(provider, system, userdata)
        self.level = 2
        self.opcode = 12
        self.timecreated = system[7]

    def checkEvent(self, date):
        good = False
        if self.checkEventTime(date):
            if self.system[1].text == "31":
                print('Se ha producido un error en una actualización')
                if self.userdate:
                    print(self.userdate[0].text)
                good = True
            elif self.system[1].text == "25":
                print('Se ha producido un error en una actualización (No se puede obtener la causa)')
                good = True
        return good
