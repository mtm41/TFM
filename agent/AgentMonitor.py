import urllib
from datetime import time, datetime
from winreg import ConnectRegistry, HKEY_LOCAL_MACHINE, OpenKey, EnumKey, QueryValueEx
from xml.etree import ElementTree

import win32api
import win32con
import win32service

from DatabaseConnection import DatabaseConnection
from Event import Event
import winapps as winapps
import os.path
import wmi as wmi

from ExtDevEvent import ExtDevEvent
from FirewallEvent import FirewallEvent
from InstallEvent import InstallEvent
from SelfInstallEvent import SelfInstallEvent
from SelfInstallWarnEvent import SelfInstallWarnEvent
from SysmonEvent import SysmonEvent
from SystemUpdateEvent import SystemUpdateEvent
from WindowsUpdateErrorEvent import WindowsUpdateErrorEvent
from Winservice import Winservice
import win32evtlog


class AgentMonitor(Winservice):
    _svc_name_ = "AgentMonitor"
    _svc_display_name_ = "Agent Monitor"

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    def main(self):
        logtypes = ['Microsoft-Windows-DriverFrameworks-UserMode/Operational']
        while self.isrunning:
            c = DatabaseConnection(DatabaseConnection.dbFile)
            c.close()
            self.mngInstalledSoftware()
            self.mngUpdates()
            date = datetime.utcnow()
            self.mngFirewall()
            self.mngNetworkConnections()
            externalDeviceAlerts = []

            time.sleep(300)

    def mngNetworkConnections(self):
        logtype = 'Microsoft-Windows-Sysmon/Operational'
        self.searchEvents(datetime.utcnow(), logtype)

    def mngFirewall(self):
        services = {"mpssvc": "El firewall de windows se encuentra desactivado"}
        for service in services.keys():
            self.checkServiceIsDisabled(service, services[service])
        self.searchEvents(datetime.utcnow(), "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall")

    def checkInstalledPrograms(self, empty):
        review = False
        installedApps = {}
        appsToWrite = []
        appList = "C:\\installedSoftware.txt"

        aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)

        winRegs = [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                   r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"]

        for winReg in winRegs:
            aKey = OpenKey(aReg, winReg)
            for i in range(1024):
                try:
                    asubkey_name = EnumKey(aKey, i)
                    asubkey = OpenKey(aKey, asubkey_name)
                    name = QueryValueEx(asubkey, "DisplayName")
                    version = QueryValueEx(asubkey, "DisplayVersion")
                    installedApps[name[0]] = version
                    if not empty:
                        f = open(appList, "r")
                        found = False
                        lines = f.readlines()
                        for line in lines:
                            if line.strip() == str(name[0]):
                                found = True
                                break
                        newInstalled = not found
                        if newInstalled:
                            review = True
                        f.close()
                    else:
                        appsToWrite.append(name[0])
                except EnvironmentError:
                    message = 'An error happened when reading {} file'.format(appList)
                    print(message)

        f = open(appList, 'w')
        for installedApp in installedApps.keys():
            f.write(installedApp)
            f.write('\n')

        f.close()

        self.mngAntivirus(installedApps)

        return review

    # This method will perform a series of operations to conclude if antivirus software is
    # up to date or not
    def mngAntivirus(self, installedApps):
        antivirus = self.checkAntivirusInstalled(installedApps)
        if antivirus:
            print('Antivirus encontrados')
            print(antivirus)
            activeServices = self.ListServices()
            actualAntivirusVersions = self.getAntivirusVersion(activeServices)
            print(actualAntivirusVersions)
            for antivirusNameInstalled in antivirus.keys():
                for actualAntivirusVersion in actualAntivirusVersions.keys():
                    if actualAntivirusVersion.capitalize() in antivirusNameInstalled.capitalize():
                        print('We have obtained last version for installed antivirus')
                        if antivirus[antivirusNameInstalled][0] >= actualAntivirusVersions[actualAntivirusVersion]:
                            print('Antivirus Software is up to date')
                        else:
                            print('Antivirus Software is NOT up to date, we need to upgrade')

    def ListServices(self):
        accessSCM = win32con.GENERIC_READ

        # Open Service Control Manager
        hscm = win32service.OpenSCManager(None, None, accessSCM)

        # Enumerate Service Control Manager DB
        typeFilter = win32service.SERVICE_WIN32
        stateFilter = win32service.SERVICE_STATE_ALL
        statuses = win32service.EnumServicesStatus(hscm, typeFilter, stateFilter)

        return statuses

    # This method will request actual antivirus software version
    def getAntivirusVersion(self, statuses):
        antivirusUrls = {"avast": "https://avast.en.softonic.com/",
                         "norton": "https://norton-antivirus.en.softonic.com/",
                         "panda": "https://panda-free-antivirus.en.softonic.com/",
                         "kapersky": "https://kaspersky-anti-virus.en.softonic.com/"}

        antivirusVersions = {}

        for (short_name, desc, status) in statuses:
            if "Antivirus" in short_name:
                print('Se ha encontrado un servicio antivirus:')
                print(short_name, desc, status)
                canReadVersion = False
                antivirusRead = ""
                for antivirusTemplate in antivirusUrls.keys():
                    if antivirusTemplate in short_name:
                        canReadVersion = True
                        antivirusRead = antivirusTemplate
                if canReadVersion:
                    print('Podemos obtener la versión')
                    found = False
                    fp = urllib.request.urlopen(antivirusUrls[antivirusRead])
                    mybytes = fp.read()

                    mystr = mybytes.decode("utf8")
                    fp.close()

                    index = mystr.find("<h3 class=\"app-specs__title\">Version")
                    version = ""
                    if index != -1:
                        i = 75
                        while not found:
                            if mystr[index + i] != '<':
                                version += mystr[index + i]
                            else:
                                found = True
                            i = i + 1
                    antivirusVersions[antivirusRead] = version

        return antivirusVersions

    # If antivirus exists, this method will return {'antivirus_name': 'antivirus_version'}
    def checkAntivirusInstalled(self, installedApps):
        antivirus = {}
        for app in installedApps.keys():
            if "Antivirus" in str(app):
                print('Antivirus installation found')
                print(app)
                antivirus[str(app)] = installedApps[app]
        return antivirus

    def mngInstalledSoftware(self):
        try:
            appList = "C:\\installedSoftware.txt"
            if not os.path.isfile(appList):
                print('File does not exist')
                self.checkInstalledPrograms(True)
            else:
                print('File exists')
                if self.checkInstalledPrograms(False):
                    print('Possible installation')
                    self.searchNormalEvents(datetime.utcnow(), "Application", "MsiInstaller")
        except:
            print("Error listando apps instaladas")

    def checkServiceIsDisabled(self, service, message):
        disabled = False
        isuphandle = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\"
                                           + service, 0, win32con.KEY_READ)
        isuptype = win32api.RegQueryValueEx(isuphandle, "Start")[0]
        win32api.RegCloseKey(isuphandle)
        if isuptype == 4:
            print(message)
            disabled = True

        return disabled

    def mngUpdates(self):
        print('Check actualizaciones')
        updatesEnabled = False
        services = {"wuauserv": "El servicio de actualizaciones automáticas se encuentra desactivado"}

        for service in services.keys():
            self.checkServiceIsDisabled(service, services[service])

        date = datetime.utcnow()
        self.searchNormalEvents(date, "System", "Microsoft-Windows-WindowsUpdateClient")
        self.searchEvents(date, "Microsoft-Windows-WindowsUpdateClient/Operational")

    def calculateOffset(self, totalRecords, eventResultSet):
        i = 0
        while True:
            try:
                totalRecords = totalRecords - i
                events = win32evtlog.EvtNext(eventResultSet, totalRecords, -1, 1)
                break
            except:
                i = i + 1
        return events

    def searchEvents(self, date, logtype):
        importantEvents = []
        eventLog = win32evtlog.EvtOpenLog(logtype, 1, None)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        totalRecords = win32evtlog.EvtGetLogInfo(eventLog, win32evtlog.EvtLogNumberOfLogRecords)[0]
        """totalRecords = win32evtlog.GetNumberOfEventLogRecords(eventLog)"""
        print("Numero de registros totales de USB's conectados: ")
        print(totalRecords)
        eventResultSet = win32evtlog.EvtQuery(logtype, 1, '*', None)
        events = self.calculateOffset(totalRecords, eventResultSet)
        totalRecords = totalRecords - len(events)
        """  else:
            events = win32evtlog.EvtNext(eventResultSet, totalRecords, -1, 1)"""
        while len(events) != 0:
            print('Vuelta')
            print(len(events))
            for event in events:
                xml = win32evtlog.EvtRender(event, 1)
                root = ElementTree.fromstring(xml)
                if logtype == "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall":
                    firewallEvent = FirewallEvent(eventLog, root[0], root[1])
                    if firewallEvent.checkEvent(date):
                        importantEvents.append(firewallEvent)
                elif logtype == "Microsoft-Windows-WindowsUpdateClient/Operational":
                    windowsUpdateError = WindowsUpdateErrorEvent(eventLog, root[0], root[1])
                    if windowsUpdateError.checkEvent(date):
                        importantEvents.append(windowsUpdateError)
                elif logtype == "Microsoft-Windows-Sysmon/Operational":
                    sysmon = SysmonEvent(eventLog, root[0], root[1])
                    if sysmon.checkEvent(date):
                        importantEvents.append(sysmon)
                else:
                    extDevEvent = ExtDevEvent(eventLog, root[0], root[1])
                    if extDevEvent.checkEvent(date):
                        importantEvents.append(extDevEvent)
            print('Antes')
            events = self.calculateOffset(totalRecords, eventResultSet)
            totalRecords = totalRecords - len(events)
            print('Despues')

    # Method for searching events from Application, Security and System categories
    def searchNormalEvents(self, date, logtype, sourceName):
        importantEvents = []
        suspiciousEvents = []
        eventLog = win32evtlog.OpenEventLog(None, logtype)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        totalRecords = win32evtlog.GetNumberOfEventLogRecords(eventLog)
        """totalRecords = win32evtlog.GetNumberOfEventLogRecords(eventLog)"""
        print("Numero de registros totales de USB's conectados: ")
        print(totalRecords)
        try:
            events = 1
            while events:
                events = win32evtlog.ReadEventLog(eventLog, flags, 0)

                for ev_obj in events:

                    if (ev_obj.SourceName == "MsiInstaller"):
                        evIns = InstallEvent(logtype, ev_obj.TimeGenerated, ev_obj.StringInserts, ev_obj.SourceName)
                        evIns.__
                        if evIns.checkEvent(date):
                            print(evIns.getSourceName())
                            importantEvents.append(evIns)
                        else:
                            suspiciousEvents.append(evIns)
                    elif ev_obj.SourceName == "Microsoft-Windows-RestartManager":
                        evIns = SelfInstallEvent(logtype, ev_obj.TimeGenerated, "", ev_obj.SourceName, ev_obj.EventID)
                        if evIns.checkEvent(date, suspiciousEvents):
                            print('Hay una posible instalación por un instalador propio')
                    elif ev_obj.SourceName == "Microsoft-Windows-User Profiles Service" \
                            and not self.checkDuplicatedSelfInstall(importantEvents) \
                            and not self.checkSuspiciousInstall(suspiciousEvents):
                        evIns = SelfInstallWarnEvent(logtype, ev_obj.TimeGenerated, "", ev_obj.SourceName, ev_obj.EventID)
                        if evIns.checkEvent(date):
                            importantEvents.append(evIns)
                            print('Hay una posible instalación de un editor no reconocido')
                    elif ev_obj.SourceName == "Microsoft-Windows-WindowsUpdateClient":
                        evIns = SystemUpdateEvent(logtype, ev_obj.TimeGenerated, ev_obj.StringInserts,
                                                  ev_obj.SourceName, ev_obj.EventID)
                        if evIns.checkEvent(date):
                            importantEvents.append(evIns)
        except:
            print('An error has happened while reading events')

    def checkDuplicatedSelfInstall(self, importantEvents):
        duplicated = False
        for event in importantEvents:
            if event.getSourceName() == "Microsoft-Windows-User Profiles Service":
                duplicated = True
                break

        return duplicated

    def checkSuspiciousInstall(self, suspiciousEvents):
        installer = False
        for event in suspiciousEvents:
            if event.getSourceName() == "MsiInstaller":
                installer = True
                break

        return installer


if __name__ == '__main__':
    AgentMonitor.parse_command_line()
