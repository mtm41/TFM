import os
import subprocess
import sys

import PySide2
from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QLineEdit, QInputDialog, QPushButton, QComboBox, QTimeEdit
from PySide2.QtCore import QFile

from AgentMonitor import AgentMonitor
from DatabaseConnection import DatabaseConnection


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        ui_file = QFile("untitled.ui")
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        button = self.window.findChild(QPushButton, "pushButton")
        button.clicked.connect(self.begin)
        ui_file.close()
        self.window.show()

        print(button)
        sys.exit(app.exec_())

    def begin(self):
        print('BUENAS')
        emailInput = self.window.findChild(QLineEdit, "test")
        devicesInput = self.window.findChild(QComboBox, "comboBox")
        devicesRespInput = self.window.findChild(QComboBox, "comboBox_8")
        installationInput = self.window.findChild(QComboBox, "comboBox_2")
        installationRespInput = self.window.findChild(QComboBox, "comboBox_9")
        firewallInput = self.window.findChild(QComboBox, "comboBox_3")
        firewallRespInput = self.window.findChild(QComboBox, "comboBox_7")
        connectionsInput = self.window.findChild(QComboBox, "comboBox_4")
        connectionsRespInput = self.window.findChild(QComboBox, "comboBox_10")
        antivirusInput = self.window.findChild(QComboBox, "comboBox_5")
        antivirusRespInput = self.window.findChild(QComboBox, "comboBox_11")
        updatesInput = self.window.findChild(QComboBox, "comboBox_6")
        updatesRespInput = self.window.findChild(QComboBox, "comboBox_12")
        api_key = self.window.findChild(QLineEdit, 'lineEdit')
        reportTime = self.window.findChild(QTimeEdit, 'timeEdit')
        email = emailInput.text()
        if not email:
            email = 'None'
        devices = str(devicesInput.currentText())
        devicesResponse = str(devicesRespInput.currentText())
        installation = str(installationInput.currentText())
        installationResponse = str(installationRespInput.currentText())
        print(installationResponse)

        firewall = str(firewallInput.currentText())
        firewallResponse = str(firewallRespInput.currentText())
        connections = str(connectionsInput.currentText())
        connectionsResponse = str(connectionsRespInput.currentText())
        firewallResponse = str(firewallRespInput.currentText())
        antivirus = str(antivirusInput.currentText())
        antivirusResponse = str(antivirusRespInput.currentText())
        updated = str(updatesInput.currentText())
        updatesResponse = str(updatesRespInput.currentText())
        api_key = str(api_key.text())
        if not api_key:
            api_key = 'None'
        reportGeneration = str(reportTime.time().toString())

        configFile = 'C:\\Program Files\\AutoDiagnose\\autodiagnose.conf'
        f = open(configFile, 'w')
        if f:
            f.write('email:{}\n'.format(email))
            f.write('devices:{}:{}\n'.format(devices, devicesResponse))
            f.write('installations:{}:{}\n'.format(installation, installationResponse))
            f.write('firewall:{}:{}\n'.format(firewall, firewallResponse))
            f.write('connections:{}:{}\n'.format(connections, connectionsResponse))
            f.write('antivirus:{}:{}\n'.format(antivirus, antivirusResponse))
            f.write('updates:{}:{}\n'.format(updated, updatesResponse))
            f.write('Report Time:{}\n'.format(reportGeneration))
            f.write('api_key:{}'.format(api_key))

        f.close()
        self.window.close()
        c = DatabaseConnection()
        c.close()
        output = os.system('dist\AgentMonitor.exe stop')
        output = os.system('dist\AgentMonitor.exe start')

        print(reportGeneration)
        os.system("SCHTASKS /CREATE /SC DAILY /TN \"My tasks2\" /TR "
                  "\"C:\\Users\\ManuelTorresMendoza\\AppData\\Local\\Programs\\Python\\Python37\\python.exe"
                  " C:\\Users\\ManuelTorresMendoza\\PycharmProjects\\agent1\\Watcher.py\" "
                  "/ST {}:{}".format(reportGeneration.split(':')[0], reportGeneration.split(':')[1]))
        #print(output)
        output = os.system('schtasks /create /tn "MyCustomTask" /sc onlogon /tr "C:\\Users\\ManuelTorresMendoza\\PycharmProjects\\agent1\\dist\\Director.exe"')
        output = os.system('dist\Director.exe')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()

    sys.exit(app.exec_())


