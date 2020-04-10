from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
                             QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
                             QVBoxLayout)

import sys



class Dialog(QDialog):
    NumGridRows = 20
    NumButtons = 4

    def __init__(self):
        super(Dialog, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.createFormGroupBox()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Form Layout - pythonspot.com")

    def createFormGroupBox(self):
        data_struct = {
            'Dispositivos externos': [self.tr('Desactivado'), self.tr('Activado')],
            'Instalaciones': ['Desactivado', 'Solo editores desconocidos', 'Activado'],
            'Activirus': ['Desactivado', 'Instalado', 'Activado'],
            'Firewall': ['Desactivado', 'Activado'],
            'Actualizaciones': ['Desactivado', 'Activado'],
            'Conexiones': ['Desactivado', 'Activado']
        }

        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Email del administrador:"), QLineEdit())
        for functionality in data_struct.keys():
            layout.addRow(QLabel('test'), QComboBox(self).addItem('asasas'))
            break
        #layout.addRow(QLabel("Age:"), QSpinBox())
        self.formGroupBox.setLayout(layout)


    def createDropDownList(self, data_struct):
        QComboBox()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())