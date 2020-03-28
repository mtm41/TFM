from datetime import datetime

from Analyzer import Analyzer

import sys

from Test import Test


def manageScan(port, analysis, ip, organization):
    begin = datetime.now()
    openPorts = analysis.scan([port])
    end = datetime.now()
    print(openPorts)
    for openPort in openPorts:
        test = Test(ip, openPort, organization, 'undefined', 'Scan', 'Exploration', str(begin), str(end), 1,
                    'Scanning says that port seems open and ready for connections', '')
        test.create()


def main():
    print(len(sys.argv))
    if len(sys.argv) <= 6:
        organization = sys.argv[3]
        ip = sys.argv[2]
        port = int(sys.argv[1])
        technology = sys.argv[4]
        domain = sys.argv[5]

        # analysis = Analyzer('Organizacion A', '192.168.1.127', 22, 'SSH', ['scan'])
        tests = ['scan']
        analysis = Analyzer(organization, ip, port, technology, tests, domain)

        manageScan(port, analysis, ip, organization)

        manageDisclosureInfo(analysis, ip, organization, port)

        manageWebServer(analysis, ip, organization, port)

        # analysis.scan([1, 22, 80, 443, 631, 57621, 1900])
        # analysis.getVersion([1, 22, 80, 443, 631, 57621, 1900])
        # analysis.checkWebHeaders()


def manageWebServer(analysis, ip, organization, port):
    begin = datetime.now()
    if analysis.checkWebServer():
        checks = analysis.checkWebHeaders()
        end = datetime.now()
        print(checks)

        for check in checks:
            print(checks[check])
            if type(checks[check]) == dict and checks[check].get('message'):
                test = Test(ip, port, organization, 'undefined', check, 'Web server headers', str(begin), str(end),
                            0, 'na', checks[check].get('message'))
                test.create()
            elif check == 'Score':
                test = Test(ip, port, organization, 'undefined', check, 'Web server headers', str(begin), str(end),
                            0, checks[check], '')
                test.create()
            else:
                test = Test(ip, port, organization, 'undefined', check, 'Web server Pentest', str(begin), str(end),
                            int(checks[check]), 'na', '')
                test.create()


def manageDisclosureInfo(analysis, ip, organization, port):
    begin = datetime.now()
    versionInfo = analysis.getVersion([port])
    end = datetime.now()
    for key in versionInfo.keys():
        print(versionInfo[key])
        for relevant in versionInfo.values():
            for relevantInfo in relevant.values():
                print(relevantInfo)
                test = Test(ip, key, organization, 'undefined', 'Banner Grabing', 'Exploration', str(begin),
                            str(end), 0,
                            'Seems that your port is disclosing information about service or distribution version',
                            relevantInfo)
                test.create()


if __name__ == '__main__':
    main()
