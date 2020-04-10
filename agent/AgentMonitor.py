import base64
import socket
import subprocess
import sys
import urllib
from datetime import time, datetime
from winreg import ConnectRegistry, HKEY_LOCAL_MACHINE, OpenKey, EnumKey, QueryValueEx
from xml.etree import ElementTree

import requests
import servicemanager
import win32api
import win32con
import win32event
import win32security
import win32service
import time

from DatabaseConnection import DatabaseConnection
import os.path

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
import win32serviceutil

class AgentMonitor(win32serviceutil.ServiceFramework):
    _svc_name_ = "AgentMonitor"
    _svc_display_name_ = "Agent Monitor"
    _svc_description_ = "My service"

    def __init__(self, args):
        self.configs = {
            'email': False,
            'devices': False,
            'installations': False,
            'firewall': False,
            'connections': False,
            'antivirus': False,
            'updates': False,
            'api_key': ''
        }
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def start(self):
        self.isrunning = True

    def readConfig(self):
        configFile = 'C:\\autodiagnose.conf'
        f = open(configFile, 'r')

        line = f.readline()
        while line:
            value = False
            data_tuple = line.split(':')
            print(data_tuple)
            print('Entra')
            if str(data_tuple[1]) == 'Activado':
                value = True
                self.configs[data_tuple[0]] = value
            elif str(data_tuple[0]) == 'api_key':
                print(data_tuple[1])
                self.configs[data_tuple[0]] = data_tuple[1]
            else:
                print('Ninguna')
                self.configs[data_tuple[0]] = value
            line = f.readline()
        f.close()

    def SvcDoRun(self):
        self.readConfig()
        self.sendSignal('start')
        rc = None
        self.isrunning = True
        while rc != win32event.WAIT_OBJECT_0:
            with open('C:\\TestService.log', 'a') as f:
                f.write('test service running...\n')
                self.main()
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)

    def SvcStop(self):
        self.sendSignal('end')
        if self.log:
            self.log.close()
        self.isrunning = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    # This method will send signals periodically to the external agent for the purpose of
    # controlling deliberately desactivation
    def sendSignal(self, mode):
        print(self.configs)
        self.log = open('C:\\autodiagnose.log', 'a')
        api_endpoint = "http://192.168.1.127:5000/api/tool/{}"
        message = socket.gethostbyname_ex(socket.gethostname())[-1]
        addr = message[len(message)-1]
        message_bytes = addr.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        api_endpoint = api_endpoint.format(base64_message)
        data = {'key': self.configs['api_key'],
                'state': mode}
        if mode == 'start' or mode == 'end':
            resp = requests.post(url=api_endpoint, verify=False, data=data)
            if resp.status_code == 200:
                self.log.write('Se ha enviado señal de {}\n'.format(mode))
                data['state'] = 'update'
                print(api_endpoint)
                print(data)
                os.system('start python CheckSignal.py {} {} {}'.format(api_endpoint, data['key'], data['state']))
            else:
                self.log.write('No se ha podido enviado señal de {}\n'.format(mode))
        elif mode == 'update':
            resp = requests.put(url=api_endpoint, verify=False, data=data)
            if resp.status_code == 200:
                self.log.write('Se ha enviado señal de {}\n'.format(mode))
            else:
                self.log.write('No se ha podido enviado señal de {}\n'.format(mode))
        else:
            self.log.write('No se ha podido interpretar el estado de la señal a enviar\n')
        self.log.close()

    def main(self):
        logtypes = ['Microsoft-Windows-DriverFrameworks-UserMode/Operational']

        while self.isrunning:
            self.log = open('C:\\autodiagnose.log', 'a')
            self.log.write('{} - Empieza nueva iteracion\n'.format(datetime.now()))
            self.c = DatabaseConnection()
            self.mngExternalDeviceCon()
            self.mngInstalledSoftware()
            self.mngUpdates()
            date = datetime.utcnow()
            self.mngFirewall()
            self.c.close()
            self.mngNetworkConnections()
            print('FIN')
            self.log.close()
            time.sleep(300)

        externalDeviceAlerts = []


    def mngExternalDeviceCon(self):
        self.log.write('{} - Comprobando nuevas conexiones de dispositivos externos\n'.format(datetime.now()))
        importantEvents = self.searchEvents(datetime.utcnow(), "Microsoft-Windows-DriverFrameworks-UserMode/Operational")
        for event in importantEvents:
            self.log.write('{} - Encontrada nueva conexion de dispositivo externo\n'.format(datetime.now()))
            sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
            print('PRUEBA')
            event_data = (event.timecreated.items()[0][1], str(event.provider), 'Se ha producido una insercion de un dispositivo externo', str(event.system[13].items()[0][1]), 'ExternalDeviceConnection')
            self.c.insert_values([event_data], sql)


    def mngNetworkConnections(self):
        self.log.write(
            '{} - Comprobando conexiones remotas\n'.format(datetime.now()))
        logtype = 'Microsoft-Windows-Sysmon/Operational'
        importantEvents = self.searchEvents(datetime.utcnow(), "Microsoft-Windows-Sysmon/Operational")
        self.c = DatabaseConnection(False)
        for event in importantEvents:
            sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
            event_data = (event.timecreated.items()[0][1], str(event.provider),
                          'Se ha producido una conexion con la IP {} catalogada como DGA'.format(event.dgaIp),
                          str(event.system[13].items()[0][1]), 'DgaConnection')
            self.c.insert_values([event_data], sql)

    # This method will check if firewall service is not enabled based on windows registry, but also if
    # firewall has been deactivated through gui by the user consulting windows event logs
    def mngFirewall(self):
        self.log.write(
            '{} - Comprobando firewall\n'.format(datetime.now()))
        services = {"mpssvc": "El firewall de windows se encuentra desactivado"}
        serviceDisabled = False
        for service in services.keys():
            serviceDisabled = self.checkServiceIsDisabled(service, services[service])

        importantEvents = self.searchEvents(datetime.utcnow(), "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall")
        sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
        if serviceDisabled:
            firewall_disabled = (str(datetime.now()), 'FirewallServiceCheck',
                                 'El servicio firewall esta desactivado', '', 'FirewallNotEnabled')
            self.c.insert_values([firewall_disabled], sql)
        for event in importantEvents:
            print('Intenta meterlo')
            print(event.userdate[6].text)
            event_data = (event.timecreated.items()[0][1], str(event.provider),
                          'Se ha desconectado el firewall {} mediante la GUI'.format(event.firewallType),
                          self.get_owner(str(event.userdate[6].text)), 'FirewallDisabledByUser')
            self.c.insert_values([event_data], sql)

    def get_owner(self, sid):
        account = subprocess.check_output(
            'whoami /user | findstr {}'.format(sid), shell=True
        )
        return account.split()[0]

    def checkInstalledPrograms(self, empty):
        self.log.write(
            '{} - Comprobando ficheros instalados\n'.format(datetime.now()))
        review = 0
        installedApps = []
        installedApps1 = {}
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
                    version = 0
                    try:
                        version = QueryValueEx(asubkey, "DisplayVersion")
                    except:
                        version = 0
                    installedApps.append(name[0])
                    installedApps1[name[0]] = version
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
                            review = review + 1
                        f.close()
                    else:
                        appsToWrite.append(name[0])
                except EnvironmentError:
                    a=1

        f = open(appList, 'w')
        for installedApp in installedApps1.keys():
            f.write(installedApp)
            f.write('\n')

        f.close()

        data = [installedApps1, review]
        return data

    # This method will perform a series of operations to conclude if antivirus software is
    # up to date or not
    def mngAntivirus(self, installedApps):
        self.log.write(
            '{} - Comprobando antivirus\n'.format(datetime.now()))
        good = False
        sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
        antivirusStatus_event = (datetime.now(), 'AntivirusCheck',
                                 'Antivirus no encontrado', '', 'AntivirusNotInstalled')
        antivirus = self.checkAntivirusInstalled(installedApps)
        if antivirus:
            print('Antivirus encontrados')
            print(antivirus)
            activeServices = self.ListServices()
            actualAntivirusVersions = self.getAntivirusVersion(activeServices)
            print(actualAntivirusVersions)
            for antivirusNameInstalled in antivirus.keys():
                antivirusStatus_event = (datetime.now(), 'AntivirusCheck',
                                         'Antivirus encontrado: {}'.format(antivirusNameInstalled),
                                         '', 'AntivirusInstalledWithoutVersion')
                for actualAntivirusVersion in actualAntivirusVersions.keys():
                    if actualAntivirusVersion.capitalize() in antivirusNameInstalled.capitalize():
                        print('We have obtained last version for installed antivirus')
                        if antivirus[antivirusNameInstalled][0] >= actualAntivirusVersions[actualAntivirusVersion]:
                            print('Antivirus Software is up to date')
                            good = True
                        else:
                            print('Antivirus Software is NOT up to date, we need to upgrade')
                            antivirusStatus_event = (datetime.now(), 'AntivirusCheck',
                                                     'Antivirus encontrado: {} {}'
                                                     .format(antivirusNameInstalled,antivirus[antivirusNameInstalled][0]),
                                                     '', 'AntivirusNotUpToDate')

        if not good:
            self.c.insert_values([antivirusStatus_event], sql)

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
        antivirusServiceFound = False

        for (short_name, desc, status) in statuses:
            if "Antivirus" in short_name:
                antivirusServiceFound = True
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

        if not antivirusServiceFound:
            sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
            antivirusServiceEvent = (str(datetime.now()), 'AntivirusServiceCheck', '', '', 'AntivirusNotPresent')
            self.c.insert_values([antivirusServiceEvent], sql)

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
            self.log.write('{} - Comprobando programas instalados\n'.format(datetime.now()))
            appList = "C:\\installedSoftware.txt"
            if not os.path.isfile(appList):
                self.log.write('{} - El fichero de registro de archivos no se encuentra\n'.format(datetime.now()))
                print('File does not exist')
                data_tuple = self.checkInstalledPrograms(True)
                self.mngAntivirus(data_tuple[0])
            else:
                self.log.write('{} - El fichero de registro de archivos se ha encuentrado\n'.format(
                    datetime.now()))
                print('File exists')
                data_duple = self.checkInstalledPrograms(False)
                self.mngAntivirus(data_duple[0])
                newSoftwareN = data_duple[1]
                print(newSoftwareN)
                if newSoftwareN > 0:
                    self.log.write('{} - Posible instalacion encontrada\n'.format(
                        datetime.now()))
                    print('Possible installation')
                    importantEvents = self.searchNormalEvents(datetime.utcnow(), "Application", "MsiInstaller")
                    sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
                    event_data = (datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 'InstallationDetection',
                                  str(newSoftwareN), '', 'NewInstallationDetection')
                    print(event_data)
                    self.c.insert_values([event_data], sql)
                    for event in importantEvents:
                        incident = ''
                        desc = 'Se ha producido una instalacion '
                        if type(event) == InstallEvent:
                            incident = 'NewInstallation'
                            desc += ' a traves del instalador de Windows, siendo un editor conocido'
                        elif type(event) == SelfInstallEvent:
                            incident = 'NewInstallationFromOwnInstaller'
                            desc += ' '
                        else:
                            incident = 'NewInstallationFromKnownEditor'
                        print('LLEGA')
                        print(event.timecreated)
                        if event.userdate is None:
                            event.userdate = ''
                        else:
                            event.userdate = event.userdate[0]
                        print(event.userdate)
                        event_data = (str(event.timecreated), str(event.provider),
                                        'Se ha producido una instalacion {}'.format(event.userdate),
                                        'Local', incident)
                        print(event_data)
                        self.c.insert_values([event_data], sql)
        except Exception as e:
            print(e)

    # This method will determine if service is enabled or not based on windows registry information
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

    # This method will search the windows update service in windows registry to determina
    # if this is enabled or not (deactivated). Moreover, it will search events related to
    # windows update (errors and performed successfully)
    def mngUpdates(self):
        self.log.write(
            '{} - Comprobando actualizaciones\n'.format(datetime.now()))
        print('Check actualizaciones')
        sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
        services = {"wuauserv": "El servicio de actualizaciones automáticas se encuentra desactivado"}

        for service in services.keys():
            if self.checkServiceIsDisabled(service, services[service]):
                updatesDisable = (datetime.now(), 'ServiceUpdateCheck', '', '', 'UpdatesNotEnabled')
                self.c.insert_values([updatesDisable], sql)

        date = datetime.utcnow()
        importantEvents = self.searchNormalEvents(date, "System", "Microsoft-Windows-WindowsUpdateClient")
        for updateEvent in importantEvents:
            updateEvent_tuple = (str(updateEvent.timecreated), updateEvent.provider, updateEvent.data, 'System', 'LastUpdate')
            self.c.insert_values([updateEvent_tuple], sql)

        importantEvents = self.searchEvents(date, "Microsoft-Windows-WindowsUpdateClient/Operational")
        for updateEvent in importantEvents:
            updateEvent_tuple = (updateEvent.timecreated.items()[0][1], updateEvent.provider,
                                 updateEvent.userdate[0], 'System', 'UpdateFailed')
            self.c.insert_values([updateEvent_tuple], sql)

    # Iterator for pywin32 evtlog function
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

    # Method for searching software self generated events.
    def searchEvents(self, date, logtype):
        importantEvents = []
        eventLog = win32evtlog.EvtOpenLog(logtype, 1, None)
        totalRecords = win32evtlog.EvtGetLogInfo(eventLog, win32evtlog.EvtLogNumberOfLogRecords)[0]
        """totalRecords = win32evtlog.GetNumberOfEventLogRecords(eventLog)"""
        print("Numero de registros totales de USB's conectados: ")
        print(totalRecords)
        eventResultSet = win32evtlog.EvtQuery(logtype, 1, '*', None)
        events = self.calculateOffset(totalRecords, eventResultSet)
        totalRecords = totalRecords - len(events)

        while len(events) != 0:
            print('Vuelta')
            print(len(events))
            for event in events:
                xml = win32evtlog.EvtRender(event, 1)
                root = ElementTree.fromstring(xml)
                sourceName = self.getClassFromSourceEvent(logtype, 1)
                evClass = globals()[sourceName]
                evIns = evClass(logtype, root[0], root[1])
                if evIns.checkEvent(date):
                    importantEvents.append(evIns)
            print('Antes')
            events = self.calculateOffset(totalRecords, eventResultSet)
            totalRecords = totalRecords - len(events)
            print('Despues')

        return importantEvents

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
                    sourceName = self.getClassFromSourceEvent(ev_obj.SourceName, 0)
                    if sourceName is not None:
                        evClass = globals()[sourceName]
                        if ev_obj.RecordNumber == 83400:
                            print(ev_obj.TimeGenerated)
                        evIns = evClass(logtype, ev_obj.TimeGenerated, ev_obj.StringInserts, ev_obj.SourceName, ev_obj.EventID)
                        if evIns.checkEvent(date, suspiciousEvents, importantEvents) \
                                and ev_obj.SourceName != 'Microsoft-Windows-RestartManager':
                            importantEvents.append(evIns)
                            if ev_obj.SourceName == 'MsiInstaller':
                                suspiciousEvents.append(evIns)


        except:
            print('An error has happened while reading events')

        return importantEvents


    def getClassFromSourceEvent(self, SourceName, type):
        classname = None
        sourceNameClassNormal = {
            'MsiInstaller': 'InstallEvent',
            'Microsoft-Windows-RestartManager': 'SelfInstallEvent',
            'Microsoft-Windows-User Profiles Service': 'SelfInstallWarnEvent',
            'Microsoft-Windows-WindowsUpdateClient': 'SystemUpdateEvent'
        }
        sourceNameClassOthers = {
            'Microsoft-Windows-Windows Firewall With Advanced Security/Firewall': 'FirewallEvent',
            'Microsoft-Windows-Sysmon/Operational': 'SysmonEvent',
            'Microsoft-Windows-DriverFrameworks-UserMode/Operational': 'ExtDevEvent',
            "Microsoft-Windows-WindowsUpdateClient/Operational": 'WindowsUpdateErrorEvent'
        }
        sourceNames = [sourceNameClassNormal, sourceNameClassOthers]
        for key in sourceNames[type].keys():
            if key == SourceName:
                classname = sourceNames[type][key]

        return classname


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AgentMonitor)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AgentMonitor)
