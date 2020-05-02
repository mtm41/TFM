import urllib
import socket
import ssl
import requests

from DgaDomainModel import DgaDomainModel
from DgaRequest import DgaRequest
from Event import Event


class SysmonEvent(Event):
    def __init__(self, provider, system, userdata):
        super().__init__(provider, system, userdata)
        self.level = 4
        self.opcode = 0
        self.timecreated = system[7]
        self.dgaRequest = DgaRequest.instance
        self.dgaIp = ''

    def formatCookie(self, cookie):
        i = 0
        begin = False
        formatedCookie = ""
        while cookie[i] != ';':
            if begin:
                formatedCookie += cookie[i]
            elif cookie[i] == '=':
                begin = True
            i = i+1
        return formatedCookie

    def calculateReqParameters(self):
        context = ssl.SSLContext()
        fp = urllib.request.urlopen('https://www.dgaintel.com/', context=context)
        mybytes = fp.read()
        cookie = self.formatCookie(fp.info()['Set-Cookie'])
        print('OK2')
        mystr = mybytes.decode("utf8")
        fp.close()
        index = mystr.find("<input id=\"csrf_token\" name=\"csrf_token\" type=\"hidden\" value=\"")
        index = index + 62
        print('OK3')
        csrf_token = ""
        csrf_tokenLength = 91
        while csrf_tokenLength > 0:
            csrf_token += mystr[index]
            index = index + 1
            csrf_tokenLength = csrf_tokenLength - 1
        print('OK4')
        print(csrf_token)
        print(cookie)
        self.dgaRequest = DgaRequest(cookie, csrf_token).instance
        print('Done')

    def makePost(self, ip):
        dga = False

        cookies = {
            'session': self.dgaRequest.getCookie(),
        }

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'https://www.dgaintel.com',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Mobile Safari/537.36',
            'Sec-Fetch-Dest': 'document',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Referer': 'https://www.dgaintel.com/',
            'Accept-Language': 'es-ES,es;q=0.9',
        }

        data = {
            'csrf_token': self.dgaRequest.getToken(),
            'domain': ip,
            'submit': 'Classify'
        }
        response = requests.post('https://www.dgaintel.com/', verify=False, headers=headers, cookies=cookies, data=data)

        # extracting response text
        pastebin_url = response.text
        index = pastebin_url.find("<h4>Prediction</h4>")
        interestingText = pastebin_url[index:len(pastebin_url)-1]

        print(interestingText)
        print(ip)
        if "dga" in interestingText:
            print('PELIGRO! POSIBLE DGA CONECTADO')
            dga = True
        else:
            print('IS LEGIT')

        return dga

    def checkEvent(self, date, lastCheck):
        good = False
        if self.checkEventTime(date, lastCheck):
            if self.system[1].text == "3":
                print('Se ha producido una conexión')
                ipList = socket.gethostbyname_ex(socket.gethostname())[-1]
                print(ipList)

                possibleDGA = self.userdate[14].text
                if self.dgaRequest is None or self.dgaRequest.checkDate():
                    self.calculateReqParameters()

                for ip in ipList:
                    if ip == self.userdate[14].text:
                        possibleDGA = self.userdate[9].text
                        domain = self.userdate[10].text

                if ip == self.userdate[9].text:
                    possibleDGA = self.userdate[14].text
                    domain = self.userdate[15].text
                else:
                    possibleDGA = self.userdate[9].text
                    domain = self.userdate[10].text

                print('Empieza')
                self.dgaIp = possibleDGA
                if domain == '':
                    domain = socket.gethostbyaddr(possibleDGA)
                dgaDomain = DgaDomainModel(possibleDGA, domain)
                print('B1')
                if dgaDomain.isActive() and dgaDomain.read():
                    if dgaDomain.dga:
                        print('Alerta: IP recogida como DGA')
                        good = True
                    else:
                        print('IP LEGÍTIMA')
                elif dgaDomain.exists():
                    print('Necesaria actualizacion')
                else:
                    print('IP EXTERNA: %s' % possibleDGA)
                    good = self.makePost(domain)
                    dgaDomain = DgaDomainModel(possibleDGA, domain, good, str(date))
                    dgaDomain.createDgaDomain()

        return good
