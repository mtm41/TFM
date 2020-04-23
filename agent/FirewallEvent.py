from Event import Event


class FirewallEvent(Event):
    def __init__(self, provider, system, userdata):
        super().__init__(provider, system, userdata)
        self.level = 4
        self.opcode = 0
        self.timecreated = system[7]
        self.firewallType = ''

    def checkEvent(self, date):
        good = False
        firewallTypes = {
            "1": "Domain Firewall",
            "2": "Internal Network Firewall",
            "4": "Public Network Firewall"
        }
        if self.checkEventTime(date) and self.system[1].text == "2003":
            if self.userdate[3].text == "00000000":
                good = True
                self.firewallType = firewallTypes[self.userdate[0].text]
                print('Alerta: Firewall' + firewallTypes[self.userdate[0].text] + ' desactivado en los últimos 5 minutos')
        return good