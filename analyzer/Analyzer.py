import socket, threading
import subprocess

import requests


class Analyzer:

    def __init__(self, organization, ip, port, tech, tests, domain):
        self.organization = organization
        self.ip = ip
        self.port = port
        self.tech = tech
        self.tests = tests
        self.domain = domain

    def TCPConnect(self, ip, port, delay, listeningPorts):

        TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPsock.settimeout(delay)
        try:
            TCPsock.connect((ip, port))
            listeningPorts.append(port)
        except:
            exit(0)

    def checkWebServer(self):
        webServer = False
        cmd = 'echo -en \"GET / HTTP/1.1\n\n\n\"| nc {} {}'.format(self.ip, self.port)
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        if str(out).find('HTTP') > -1:
            webServer = True

        return webServer

    def scan(self, ports):
        delay = 1000
        threads = []
        listeningPorts = []

        for port in ports:
            print(port)
            t = threading.Thread(target=self.TCPConnect, args=(self.ip, port, delay, listeningPorts))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            print('UNION')
            thread.join()
            print(listeningPorts)

        return listeningPorts

    def getVersion(self, ports):
        result = {}
        distributions = [
            'Ubuntu',
            'Debian',
            'Windows',
            'Centos',
            'RHEL',
            'Gentoo',
            'BSD'
        ]

        for port in ports:
            distributionFound = False
            if self.checkWebServer():
                print('WEB SERVER')
                cmd = 'echo -en \"GET / HTTP/1.1\n\n\n\"| nc {} {} |grep Server | head -1'.format(self.ip, port)
                proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
            else:
                cmd = 'nc -v -n -w 1 {} {}'.format(self.ip, port)
                print(cmd)
                proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()

            res = str(out)
            print(res)
            numberFound = False
            versionFound = False
            for character in res:
                if '0' <= character <= '9':
                    numberFound = True
                elif numberFound and character == '.':
                    versionFound = res
                    alert = 'Es muy probable que muestres la version del servicio en el puerto {}'.format(port)
                    print(alert)
                    break
                else:
                    numberFound = False

            for distribution in distributions:
                if str(res).find(distribution) > -1:
                    message = 'Se ha encontrado la distribución de la maquina {}'.format(distribution)
                    distributionFound = distribution
                    print(message)

            result[port] = {
                'VersionFound': versionFound,
                'Distribucion': distributionFound
            }

        print(result)
        return result

    def checkCookie(self, output):
        secureCookie = False
        cmd = 'echo {} | grep cookie'.format(output)
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if len(str(out)) > 2:
            if str(out).find('HttpOnly') > -1:
                print('Hay cookie seguro')
                secureCookie = True
        else:
            print('Parece que no hay cabecera de cookies')

        return secureCookie

        return False
    def checkWebHeaders(self):
        checks = {
            'HttpsEnabled': False,
            'HttpsRedirection': False,
            'SecuredCookie': False,
            'ETag': False,
            'X-Powered-By': False,
            'Score': ''
        }

        cmd = 'curl --head https://www.google.es'
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        firstLine = str(out).split("\\r")[0]

        # Looking for 200 code
        if firstLine.find('20') > -1:
            checks['HttpsEnabled'] = True
            checks['SecuredCookie'] = self.checkCookie(str(out))
            firstLine = str(out).split("\\r")[0]

            # Redirection
            if str(firstLine).find('30') > -1 and str(out).find('Location: https://') > -1:
                checks['HttpsRedirection'] = True

            other_security_risks = ['ETag', 'X-Powered-By']
            for risk in other_security_risks:
                if str(out).find(risk) > -1:
                    checks[risk] = True

        securityHeadersURL = 'https://securityheaders.com/?q={}&followRedirects=on'.format('www.ua.es')

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0(X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml; q = 0.9, image/webp, */*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': securityHeadersURL,
        }

        response = requests.get(securityHeadersURL, headers=headers)

        index = response.text.find('<div class="score_')
        if index > -1:
            index = index+18
            section = response.text[index:index+40]
            for score in ['A', 'B', 'C', 'D', 'E', 'F']:
                searched = '<span>{}</span>'.format(score)
                if section.find(searched) > -1:
                    checks['Score'] = score
                    break

        possibleInfo = [
            'Missing Headers',
            'Upcoming Headers',
            'Additional Information'
        ]

        section = ''
        for info in possibleInfo:
            searched = "<div class=\"reportTitle\">{}</div>".format(info)
            index0 = response.text.find(searched)
            if index0 > -1:
                section = response.text[index0 + len(searched):]

                # Looking for detailed information (advices)
                structureToSearch = "<th class=\"tableLabel table_" # Advice Row (No matter blue, orange or red)
                index1 = section.find(structureToSearch)
                while index1 > -1:
                    section = section[index1 + len(structureToSearch):]

                    # Get type of advice
                    adviceType = ''
                    adviceTypes = ['blue', 'red', 'orange', 'green']
                    for element in adviceTypes:
                        if section[0:7].find(element) > -1:
                            adviceType = element
                            break

                    if adviceType != 'green':
                        # Get header Name
                        begin = False
                        header = ''
                        for character in section:
                            if character == '>':
                                begin = True
                            elif character == '<':
                                break
                            elif begin:
                                header += character

                        # Advice content for header found
                        index2 = section.find("</a>")
                        if index2 > -1:
                            index2 += 4
                            advice = ''
                            for character in section[index2:]:
                                if character != '<':
                                    advice += character
                                else:
                                    break
                            checks[header] = {'type': adviceType, 'message': advice}
                    index1 = section.find(structureToSearch) # Next row

        return checks
