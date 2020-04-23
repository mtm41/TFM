import os
import subprocess
import sys

import PySide2
from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QLineEdit, QInputDialog, QPushButton, QComboBox
from PySide2.QtCore import QFile

from AgentMonitor import AgentMonitor


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
        installationInput = self.window.findChild(QComboBox, "comboBox_2")
        firewallInput = self.window.findChild(QComboBox, "comboBox_3")
        connectionsInput = self.window.findChild(QComboBox, "comboBox_4")
        antivirusInput = self.window.findChild(QComboBox, "comboBox_5")
        updatesInput = self.window.findChild(QComboBox, "comboBox_6")
        api_key = self.window.findChild(QLineEdit, 'lineEdit')
        email = emailInput.text()
        devices = str(devicesInput.currentText())
        installation = str(installationInput.currentText())
        firewall = str(firewallInput.currentText())
        connections = str(connectionsInput.currentText())
        antivirus = str(antivirusInput.currentText())
        updated = str(updatesInput.currentText())

        configFile = 'C:\\autodiagnose.conf'
        f = open(configFile, 'w')
        if f:
            f.write('email:{}\n'.format(email))
            f.write('devices:{}\n'.format(devices))
            f.write('installations:{}\n'.format(installation))
            f.write('firewall:{}\n'.format(firewall))
            f.write('connections:{}\n'.format(connections))
            f.write('antivirus:{}\n'.format(antivirus))
            f.write('updates:{}\n'.format(updated))
            f.write('api_key:{}\n'.format(api_key))

        self.window.close()
        output = os.system('dist\AgentMonitor.exe stop')
        output = os.system('dist\AgentMonitor.exe start')

        print(output)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()

    sys.exit(app.exec_())


