from datetime import time, datetime
from xml.etree import ElementTree

from Event import Event
import winapps as winapps
import os.path
import wmi as wmi

from ExtDevEvent import ExtDevEvent
from InstallEvent import InstallEvent
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
            self.mngInstalledSoftware()
            externalDeviceAlerts = []
            date = datetime.utcnow()
            """ self.searchEvents(date, logtypes[0])"""
            time.sleep(300)

    def mngInstalledSoftware(self):
        try:
            appList = "C:\\installedSoftware.txt"
            regExist = True
            appNumber = 0
            if not os.path.isfile(appList):
                print('File does not exist')
                f = open(appList, "+w")
                f.close()
                regExist = False
            else:
                appNumber = sum(1 for line in open(appList, "+r"))
                actualAppNumber = winapps.list_installed().__sizeof__()
                if appNumber != actualAppNumber:
                    print('Possible installation')
                    self.searchNormalEvents(datetime.utcnow(), "Application", "MsiInstaller")
            print(sum(1 for line in open(appList, "+r")))
            print(winapps.list_installed().__sizeof__())

        except:
            print("Error listando apps instaladas")

    def searchEvents(self, date, logtype):
        eventLog = win32evtlog.EvtOpenLog(logtype, 1, None)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        totalRecords = win32evtlog.EvtGetLogInfo(eventLog, win32evtlog.EvtLogNumberOfLogRecords)[0]
        """totalRecords = win32evtlog.GetNumberOfEventLogRecords(eventLog)"""
        print("Numero de registros totales de USB's conectados: ")
        print(totalRecords)
        eventResultSet = win32evtlog.EvtQuery(logtype, 1, '*', None)
        events = win32evtlog.EvtNext(eventResultSet, totalRecords, -1, 1)
        for event in events:
            xml = win32evtlog.EvtRender(event, 1)
            root = ElementTree.fromstring(xml)

            if logtype == "Application":
                print('OK')
                installEvent = InstallEvent(logtype, root[0], root[1])
                installEvent.checkEvent(date)

            extDevEvent = ExtDevEvent(eventLog, root[0], root[1])
            extDevEvent.checkEvent(date)





    def searchNormalEvents(self, date, logtype, sourceName):
        eventLog = win32evtlog.OpenEventLog('localhost', logtype)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        totalRecords = win32evtlog.GetNumberOfEventLogRecords(eventLog)
        """totalRecords = win32evtlog.GetNumberOfEventLogRecords(eventLog)"""
        print("Numero de registros totales de USB's conectados: ")
        print(totalRecords)
        try:
            events = 1
            while events:
                events = win32evtlog.ReadEventLog(eventLog,flags,0)

                for ev_obj in events:
                    if ev_obj.StringInserts:
                        evIns = InstallEvent(logtype, ev_obj.TimeGenerated, ev_obj.StringInserts[0], ev_obj.SourceName)
                        if evIns.checkEvent(date):
                            print(ev_obj.StringInserts[0])
        except:
            print('An error has happened while reading events')

if __name__ == '__main__':
    AgentMonitor.parse_command_line()
