import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml

from Analyzer import Analyzer

import sys

from Organization import Organization
from Test import Test


def manageScan(port, analysis, ip, organization):
    begin = datetime.now()
    openPorts = analysis.scan([port])
    end = datetime.now()
    open = False
    message = 'Scanning says that port seems clossed'
    if len(openPorts) > 0:
        open = True
        message = 'Scanning says that port seems open and ready for connections'
    test = Test(ip, port, organization, 'undefined', 'Scan', 'Exploration', str(begin), str(end), 1,
                message, '')
    test.create()

    return open


def main():
    if len(sys.argv) <= 6:
        organization = sys.argv[3]
        ip = sys.argv[2]
        port = int(sys.argv[1])
        technology = sys.argv[5]
        domain = sys.argv[4]

        # analysis = Analyzer('Organizacion A', '192.168.1.127', 22, 'SSH', ['scan'])
        tests = ['scan']
        analysis = Analyzer(organization, ip, port, technology, tests, domain)
        # checking type of test, for example, monitoring
        if technology == 'Monitoring':
            sendAlert(organization, ip)
        elif manageScan(port, analysis, ip, organization):
            manageDisclosureInfo(analysis, ip, organization, port)
            manageWebServer(analysis, ip, organization, port)

        # analysis.scan([1, 22, 80, 443, 631, 57621, 1900])
        # analysis.getVersion([1, 22, 80, 443, 631, 57621, 1900])
        # analysis.checkWebHeaders()

def sendAlert(organization, ip):
    email = Organization(organization).getEmail()
    message = "The remote host didn't send an update signal, the tool could has been powered off"
    if email is not None:
        sent = True
        try:
            conf = yaml.load(open('application.yml'))
            emailUser = conf['user_smtp']['email']
            pwd = conf['user_smtp']['password']
            gateway = smtplib.SMTP(host='smtp.gmail.com', port=587)
            gateway.starttls()
            gateway.login(emailUser, pwd)

            msg = MIMEMultipart('alternative')
            msg['From'] = 'auto.diagnose.tool.tfm@gmail.com'
            msg['To'] = email
            subject = 'Alert happened in local host {}'.format(ip)
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'html'))

            gateway.send_message(msg)
        except Exception as ex:
            print(ex)
            sent = False

    return sent

def manageWebServer(analysis, ip, organization, port):
    begin = datetime.now()
    if analysis.checkWebServer():
        checks = analysis.checkWebHeaders()
        end = datetime.now()

        for check in checks:
            if type(checks[check]) == dict and checks[check].get('message'):
                test = Test(ip, port, organization, 'undefined', check, 'Web server headers', str(begin), str(end),
                            0, checks[check].get('message'), checks[check].get('message'))
                test.create()
            elif check == 'Score':
                test = Test(ip, port, organization, 'undefined', check, 'Web server headers', str(begin), str(end),
                            0, checks[check], '')
                test.create()
            else:
                if int(checks[check]) == 1:
                    state = 'Enabled'
                else:
                    state = 'Disabled'
                test = Test(ip, port, organization, 'undefined', check, 'Web server Pentest', str(begin), str(end),
                            int(checks[check]), state, '')
                test.create()


def manageDisclosureInfo(analysis, ip, organization, port):
    begin = datetime.now()
    versionInfo = analysis.getVersion([port])
    end = datetime.now()
    for key in versionInfo.keys():
        for relevant in versionInfo.values():
            for relevantInfo in relevant.values():
                print(relevantInfo)
                test = Test(ip, key, organization, 'undefined', 'Banner Grabing', 'Exploration', str(begin),
                            str(end), 0,
                            'Seems that your port is disclosing information about service or distribution version.'
                            + relevantInfo,
                            relevantInfo)
                test.create()


if __name__ == '__main__':
    main()
