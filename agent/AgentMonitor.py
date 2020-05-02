import base64
import socket
import subprocess
import sys
import threading
import urllib
from datetime import time, datetime
from multiprocessing.connection import Client
from os import path
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

from Logger import Logger, States
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
        self.log = Logger()
        self.sendSignalTime = ''
        self.configs = {
            'email': False,
            'devices': False,
            'installations': False,
            'firewall': False,
            'connections': False,
            'antivirus': False,
            'updates': False,
            'api_key': '',
            'Report Time': '12:00:00'
        }
        self.responses = {
            'devices': None,
            'installations': None,
            'firewall': None,
            'connections': None,
            'antivirus': None,
            'updates': None
        }
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def start(self):
        self.isrunning = True

    def readConfig(self):
        try:
            if not path.exists('C:\\Program Files\\AutoDiagnose'):
                os.mkdir('C:\\Program Files\\AutoDiagnose')
            self.log.write(States.READING_CONFIG.value)
            configFile = 'C:\\Program Files\\AutoDiagnose\\autodiagnose.conf'
            f = open(configFile, 'r')

            line = f.readline()
            while line:
                value = False
                data_tuple = line.split(':')
                if str(data_tuple[1]) == 'Activado':
                    value = True
                    self.configs[data_tuple[0]] = value
                    self.responses[data_tuple[0]] = data_tuple[2]
                elif str(data_tuple[1]) == 'Solo de origen desconocido' or str(data_tuple[1]) == 'Solo Instalación':
                    # Only partial functionality
                    value = 1
                    self.configs[data_tuple[0]] = value
                    self.responses[data_tuple[0]] = data_tuple[2]
                elif str(data_tuple[0]) == 'api_key':
                    self.configs[data_tuple[0]] = data_tuple[1]
                elif str(data_tuple[0]) == 'Report Time':
                    self.configs[data_tuple[0]] == data_tuple[1]
                else:
                    self.configs[data_tuple[0]] = value
                line = f.readline()
            f.close()
        except Exception as ex:
            self.log.write(States.READING_CONFIG_ERROR)
            raise Exception('No se ha podido acceder al fichero de configuracion')

    def send_alert(self, event):
        message = event[0] + ' || ' + event[2] + ' realizado por ' + event[3]
        api_endpoint = 'http://192.168.1.127:5000/api/alert/{}'
        ipList = socket.gethostbyname_ex(socket.gethostname())[-1]
        addr = ipList[len(ipList) - 1]
        ip_bytes = addr.encode('ascii')
        base64_bytes = base64.b64encode(ip_bytes)
        base64_message = base64_bytes.decode('ascii')
        api_endpoint = api_endpoint.format(base64_message)
        response = requests.post(url=api_endpoint, verify=False, data={'key': str(self.configs['api_key']), 'alert': message})
        if response.status_code == 200:
            print('Informe local enviado')
        else:
            print('Error enviando informe local')

    def SvcDoRun(self):
        self.readConfig()
        self.log.write(States.PROGRAM_INIT.value)
        self.log.write(States.SENDING_SIGNAL_START_TO_AGENT.value)
        self.sendSignal('start')
        rc = None
        self.isrunning = True
        while rc != win32event.WAIT_OBJECT_0:
            self.main()
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)

    def SvcStop(self):
        self.log.write(States.SENDING_SIGNAL_STOP_TO_AGENT.value)
        self.sendSignal('end')
        self.isrunning = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    # This method will send signals periodically to the external agent for the purpose of
    # controlling deliberately desactivation
    def sendSignal(self, mode):
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
                data['state'] = 'update'
                self.log.write(States.CHECK_SIGNAL_START.value)
                print(api_endpoint)
                started = datetime.now()
                self.sendSignalTime = datetime.now()
                rest = (started.minute + 30) % 60
                if (started.minute + 30) / 60 >= 1:
                    self.sendSignalTime = self.sendSignalTime.replace(hour=self.sendSignalTime.hour + 1)
                self.sendSignalTime = self.sendSignalTime.replace(minute=rest)
            else:
                self.log.write(States.SENDING_SIGNAL_TO_AGENT_FAILED.value)
        elif mode == 'update':
            resp = requests.put(url=api_endpoint, verify=False, data=data)
            if resp.status_code != 200:
                self.log.write(States.SENDING_SIGNAL_TO_AGENT_FAILED.value)
        else:
            self.log.write(States.SENDING_SIGNAL_TO_AGENT_FAILED.value)


    def main(self):
        lastDevicesCheck = None
        lastInstallationCheck = None
        lastUpdatesCheck = None
        lastFirewallCheck = None
        lastConnectionCheck = None
        while self.isrunning:
            self.log.write(States.ITERATION_INIT.value)
            self.c = DatabaseConnection()
            if self.configs['devices']:
                lastDevicesCheck = self.mngExternalDeviceCon(lastDevicesCheck)
            if self.configs['installations'] or self.configs['installations'] == 1:
                lastInstallationCheck = self.mngInstalledSoftware(lastInstallationCheck)
            if self.configs['updates']:
                lastUpdatesCheck = self.mngUpdates(lastUpdatesCheck)
            if self.configs['firewall']:
                lastFirewallCheck = self.mngFirewall(lastFirewallCheck)
            self.c.close()
            if self.configs['connections']:
                lastConnectionCheck = self.mngNetworkConnections(lastConnectionCheck)
            print('FIN')
            if datetime.now() >= self.sendSignalTime:
                self.sendSignal('update')
            time.sleep(60)
            if datetime.now() >= self.sendSignalTime:
                self.sendSignal('update')



    def mngExternalDeviceCon(self, lastCheck):
        self.log.write(States.CHECK_DEVICE_CONNECTIONS.value)
        actualCheck = datetime.utcnow()
        importantEvents = self.searchEvents(datetime.utcnow(), lastCheck, "Microsoft-Windows-DriverFrameworks-UserMode/Operational")
        for event in importantEvents:
            self.log.write(States.DEVICE_CONNECTION_FOUND.value)
            sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
            event_data = (str(event.timecreated.items()[0][1]), str(event.provider), 'Se ha producido una insercion de un dispositivo externo', str(event.system[13].items()[0][1]), 'ExternalDeviceConnection')
            print('SE EJECUTA')
            self.send_alert(event_data)
            self.execResponse(self.responses['devices'], 'devices')
            self.c.insert_values([event_data], sql)

        return actualCheck


    def mngNetworkConnections(self, lastCheck):
        self.log.write(States.CHECK_CONNECTIONS.value)
        actualCheck = datetime.utcnow()
        importantEvents = self.searchEvents(actualCheck, lastCheck, "Microsoft-Windows-Sysmon/Operational")
        self.c = DatabaseConnection(False)
        for event in importantEvents:
            sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
            event_data = (str(event.timecreated.items()[0][1]), str(event.provider),
                          'Se ha producido una conexion con la IP {} catalogada como DGA'.format(event.dgaIp),
                          str(event.system[13].items()[0][1]), 'DgaConnection')
            self.send_alert(event_data)
            self.execResponse(self.responses['connections'], 'connections')
            self.c.insert_values([event_data], sql)

        return actualCheck

    # This method will check if firewall service is not enabled based on windows registry, but also if
    # firewall has been deactivated through gui by the user consulting windows event logs
    def mngFirewall(self, lastCheck):
        self.log.write(States.CHECK_FIREWALL.value)
        services = {"mpssvc": "El firewall de windows se encuentra desactivado"}
        serviceDisabled = False
        for service in services.keys():
            serviceDisabled = self.checkServiceIsDisabled(service, services[service])

        actualCheck = datetime.utcnow()
        importantEvents = self.searchEvents(actualCheck, lastCheck, "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall")
        sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
        if serviceDisabled:
            firewall_disabled = (str(datetime.now()), 'FirewallServiceCheck',
                                 'El servicio firewall esta desactivado', '', 'FirewallNotEnabled')
            self.send_alert(firewall_disabled)
            self.c.insert_values([firewall_disabled], sql)
        for event in importantEvents:
            event_data = (str(event.timecreated.items()[0][1]), str(event.provider),
                          'Se ha desconectado el firewall {} mediante la GUI'.format(event.firewallType),
                          str(self.get_owner(str(event.userdate[6].text))), 'FirewallDisabledByUser')
            self.send_alert(event_data)
            self.execResponse(self.responses['firewall'], 'firewall')
            self.c.insert_values([event_data], sql)

        return actualCheck

    def get_owner(self, sid):
        account = subprocess.check_output(
            'whoami /user | findstr {}'.format(sid), shell=True
        )
        return account.split()[0]

    def checkInstalledPrograms(self, empty):
        review = 0
        installedApps = []
        installedApps1 = {}
        appsToWrite = []
        appList = "C:\\Program Files\\AutoDiagnose\\installedSoftware.txt"

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
        self.log.write(States.CHECK_ANTIVIRUS.value)
        good = False
        sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
        antivirusStatus_event = (str(datetime.now()), 'AntivirusCheck',
                                 'Antivirus no encontrado', '', 'AntivirusNotInstalled')
        antivirus = self.checkAntivirusInstalled(installedApps)
        if antivirus:
            print('Antivirus encontrados')
            print(antivirus)
            activeServices = self.ListServices()
            actualAntivirusVersions = self.getAntivirusVersion(activeServices)
            if self.configs['antivirus'] != 1: # Checking only installation option
                print(actualAntivirusVersions)
                for antivirusNameInstalled in antivirus.keys():
                    antivirusStatus_event = (str(datetime.now()), 'AntivirusCheck',
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
                                antivirusStatus_event = (str(datetime.now()), 'AntivirusCheck',
                                                         'Antivirus encontrado: {} {}'
                                                         .format(antivirusNameInstalled,antivirus[antivirusNameInstalled][0]),
                                                         '', 'AntivirusNotUpToDate')
            else:
                good = True

        if not good:
            self.send_alert(antivirusStatus_event)
            self.execResponse(self.responses['antivirus'], 'antivirus')
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
            self.send_alert(antivirusServiceEvent)
            self.execResponse(self.responses['antivirus'], 'antivirus')
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

    def mngInstalledSoftware(self, lastCheck):
        actualCheck = datetime.utcnow()
        try:
            self.log.write(States.CHECK_INSTALLATIONS.value)
            appList = "C:\\Program Files\\AutoDiagnose\\installedSoftware.txt"
            if not os.path.isfile(appList):
                self.log.write(States.CHECK_INSTALLATIONS_ERROR.value)
                data_tuple = self.checkInstalledPrograms(True)
                if self.configs['antivirus'] or self.configs['antivirus'] == 1:
                    self.mngAntivirus(data_tuple[0])
            else:
                data_duple = self.checkInstalledPrograms(False)
                if self.configs['antivirus']:
                    self.mngAntivirus(data_duple[0])
                newSoftwareN = data_duple[1]
                if newSoftwareN > 0:
                    self.log.write(States.INSTALLATION_FOUND.value)
                    actualCheck = datetime.utcnow()
                    importantEvents = self.searchNormalEvents(actualCheck, lastCheck, "Application", "MsiInstaller")
                    sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
                    event_data = (datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 'InstallationDetection',
                                  str(newSoftwareN) + ' nuevos programas instalados', '', 'NewInstallationDetection')
                    self.send_alert(event_data)
                    self.execResponse(self.responses['installations'], 'installations')
                    self.c.insert_values([event_data], sql)
                    for event in importantEvents:
                        incident = ''
                        desc = 'Se ha producido una instalacion '
                        if type(event) == InstallEvent:
                            incident = 'NewInstallation'
                            desc += ' a traves del instalador de Windows, siendo un editor conocido'
                        elif type(event) == SelfInstallEvent:
                            incident = 'NewInstallationFromOwnInstaller'
                            desc += ' a traves de un instalador propio'
                        else:
                            incident = 'NewInstallationFromKnownEditor'
                            desc += ' de un editor desconocido'
                        if event.userdate is None:
                            event.userdate = ''
                        else:
                            event.userdate = event.userdate[0]

                        event_data = (str(event.timecreated), str(event.provider),
                                        desc + ' {}'.format(event.userdate),
                                        'Local', incident)
                        print('VA A ENVIAR ALERTA')
                        if not (self.configs['installations'] == 1 and incident == 'NewInstallation'):
                            self.send_alert(event_data)
                            self.c.insert_values([event_data], sql)
        except Exception as e:
            print(e)

        return actualCheck

    # This method will determine if service is enabled or not based on windows registry information
    def checkServiceIsDisabled(self, service, message):
        disabled = False
        isuphandle = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\"
                                           + service, 0, win32con.KEY_READ)
        isuptype = win32api.RegQueryValueEx(isuphandle, "Start")[0]
        win32api.RegCloseKey(isuphandle)
        if isuptype == 4:
            disabled = True

        return disabled

    # This method will search the windows update service in windows registry to determina
    # if this is enabled or not (deactivated). Moreover, it will search events related to
    # windows update (errors and performed successfully)
    def mngUpdates(self, lastCheck):
        self.log.write(States.CHECK_UPDATES.value)
        sql = "INSERT INTO Evento VALUES(?,?,?,?,?)"
        services = {"wuauserv": "El servicio de actualizaciones automáticas se encuentra desactivado"}

        for service in services.keys():
            if self.checkServiceIsDisabled(service, services[service]):
                updatesDisable = (str(datetime.now()), 'ServiceUpdateCheck',
                                  'Las actualizaciones automaticas han sido desactivadas', '', 'UpdatesNotEnabled')
                self.send_alert(updatesDisable)
                self.execResponse(self.responses['updates'], 'updates0')
                self.c.insert_values([updatesDisable], sql)

        actualCheck = datetime.utcnow()
        importantEvents = self.searchNormalEvents(actualCheck, lastCheck, "System", "Microsoft-Windows-WindowsUpdateClient")
        for updateEvent in importantEvents:
            updateEvent_tuple = (str(updateEvent.timecreated), updateEvent.provider,
                                 'Actualizacion encontrada: ' + updateEvent.data, 'System', 'LastUpdate')
            self.send_alert(updateEvent_tuple)
            self.c.insert_values([updateEvent_tuple], sql)

        importantEvents = self.searchEvents(actualCheck, lastCheck, "Microsoft-Windows-WindowsUpdateClient/Operational")
        for updateEvent in importantEvents:
            updateEvent_tuple = (str(updateEvent.timecreated.items()[0][1]), updateEvent.provider,
                                 'Actualizacion fallida: ' + updateEvent.userdate[0], 'System', 'UpdateFailed')
            self.send_alert(updateEvent_tuple)
            self.execResponse(self.responses['updates'], 'updates1')
            self.c.insert_values([updateEvent_tuple], sql)

        return actualCheck

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
    def searchEvents(self, date, lastCheck, logtype):
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
                if evIns.checkEvent(date, lastCheck):
                    importantEvents.append(evIns)
            print('Antes')
            events = self.calculateOffset(totalRecords, eventResultSet)
            totalRecords = totalRecords - len(events)
            print('Despues')

        return importantEvents

    # Method for searching events from Application, Security and System categories
    def searchNormalEvents(self, date, lastCheck, logtype, sourceName):
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
                        if evIns.checkEvent(date, suspiciousEvents, importantEvents, lastCheck) \
                                and ev_obj.SourceName != 'Microsoft-Windows-RestartManager':
                            importantEvents.append(evIns)
                            if ev_obj.SourceName == 'MsiInstaller':
                                suspiciousEvents.append(evIns)


        except:
            self.log.write(States.ERROR_READING_EVENTS.value)

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

    def execResponse(self, activeResponse, type):
        executed = True
        print(activeResponse)
        print(type)
        if activeResponse == 'Mostrar aviso\n':
            self.log.write(States.EXECUTING_ACTION_RESPONSE_SA)
            address = ('localhost', 6000)
            conn = Client(address, authkey=b'password')
            conn.send(str(activeResponse).split('\n')[0] + ',' + type)
            conn.send('close')


        elif activeResponse == 'Desconectar red\n' or activeResponse == 'Apagar PC\n':
            if activeResponse == 'Desconectar red\n':
                self.log.write(States.EXECUTING_ACTION_RESPONSE_ND)
            else:
                self.log.write(States.EXECUTING_ACTION_RESPONSE_PO)
            self.log.write(States.EXECUTING_ACTION_RESPONSE_SA)
            address = ('localhost', 6000)
            conn = Client(address, authkey=b'password')
            conn.send(str(activeResponse).split('\n')[0] + ',' + type)
            conn.send('close')
        else:
            executed = False

        return executed


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AgentMonitor)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AgentMonitor)
