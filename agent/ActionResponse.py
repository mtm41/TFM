import os
import sys
from multiprocessing.connection import Listener

import win32file
import win32pipe
from PySide2 import QtWidgets
from PySide2.QtCore import QFile, QRunnable, QThreadPool
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QApplication, QLabel


class ActionResponse(QtWidgets.QWidget):

    def power_off(self):
        os.system("shutdown /s /t 0")

    def show_alert_window(self, alert):

        try:
            messages = {
                'devices': 'Se ha detectado una inserción de dispositivo externo en el equipo. Esta acción \n'
                           'no está contenplada en la política de seguridad del equipo, ya que puede llevar\n'
                           ' a comprometer el estado de la red entera en caso de que contenga malware, filtrar\n'
                           ' datos, o incluso destruir el equip.o',
                'installations': 'Se ha detectado una instalación en el equipo. Esta acción no está contemplada\n'
                                 ' en la política de seguridad del equipo. Las instalaciones que provienen de\n'
                                 ' editores desconocidos pueden haber sido modificadas para realzar procesos\n'
                                 ' dañinos en el equipo.',
                'firewall': 'Se ha detectado la desactivación del firewall. Esta acción no está contemplada en\n'
                            ' la política de seguridad del equipo. La desactivación del firewall de red, aun de\n'
                            ' manera momentánea, puede permitir la intrusión de agentes externos en este.',
                'antivirus': 'Se ha detectado un mal funcionamiento con el antivirus local. Bajo este estado defectuoso\n'
                             ' el equipo no debería de funcionar con todas sus funcionalidades, ya que puede facilitar\n'
                             ' la entrada de malware en este.',
                'updates0': 'Se ha detectado que el servicio de actualizaciones automáticas ha sido desactivado. \n'
                            'Esta acción no está contemplada en la política de seguridad del equipo. Un equipo\n'
                            ' desactualizado puede facilitar las intrusiones de atacantes y el mal funcionamiento.',
                'updates1': 'Se ha detectado una actualización fallida. La política de seguridad del equipo refleja\n'
                            ' que este debe de estar en todo momento actualizado. Utilizar un equipo desactualizado\n'
                            ' puede favorecer la aparición de riesgos de seguridad y malos funcionamientos.',
                'connections': 'Se ha detectado una conexión externa a un dominio catalogado como DGA. Esta situación\n'
                               ' puede ser muy perjudicial para el estado de su red, ya que estos dominios pueden\n'
                               ' contener malware que se puede haber distribuido a su equipo.'
            }
            ui_file = QFile("C:\\Program Files\\AutoDiagnose\\alert.ui")
            ui_file.open(QFile.ReadOnly)
            loader = QUiLoader()
            self.window = loader.load(ui_file)
            message = self.window.findChild(QLabel, "label_2")
            message.setText(messages[alert])
            ui_file.close()
            self.window.show()
            button = self.window.findChild(QPushButton, "pushButton")
            button.clicked.connect(self.closeWindow)

            sys.exit(app.exec_())
        except Exception as ex:
            print(ex)

    def closeWindow(self):
        self.window.close()

    def shutdown_network(self):
        os.system("wmic path win32_networkadapter where \"NetEnabled='TRUE'\" call disable")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ActionResponse()
    if sys.argv[1] == 'Apagar PC':
        widget.power_off()
    elif sys.argv[1] == 'Mostrar aviso':
        widget.show_alert_window(sys.argv[2])
    elif sys.argv[1] == 'Desconectar red':
        widget.shutdown_network()
