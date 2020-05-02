import datetime
import enum


class States(enum.Enum):
    PROGRAM_INIT = 'El servicio ha empezado a ejecutarse\n'
    READING_CONFIG = 'Leyendo fichero de configuracion\n'
    READING_CONFIG_ERROR = 'Error: No se ha podido leer el fichero de configuracion\n'
    SENDING_SIGNAL_START_TO_AGENT = 'Enviando señal de encendido al agente externo\n'
    SENDING_SIGNAL_STOP_TO_AGENT = 'Enviando señal de apagado al agente externo\n'
    SENDING_SIGNAL_TO_AGENT_FAILED = 'No se ha podido enviar la señal al agente externo\n'
    CHECK_SIGNAL_START = 'Se ha ejecutado el proceso de comprobación de señales en segundo plano\n'
    BD_CONNECTION_ERROR = 'Error: No se ha podido conectar a la base de datos\n'
    ITERATION_INIT = 'Nueva iteración de comprobaciones comienza\n'
    CHECK_DEVICE_CONNECTIONS = 'Comprobando conexiones de dispositivos externos\n'
    DEVICE_CONNECTION_FOUND = 'Se han encontrado incidios de que un dispositivo externo ha sido conectado\n'
    CHECK_INSTALLATIONS = 'Comprobando instalaciones de software\n'
    INSTALLATION_FOUND = 'Se han encontrado indicios de que se ha realizado una instalación\n'
    CHECK_INSTALLATIONS_ERROR = 'Error: No se ha podido acceder al registro de software instalado\n'
    CHECK_FIREWALL = 'Comprobando desconexiones de firewall\n'
    FIREWALL_DESACTIVATION_FOUND = 'Se han encontrado indicios de que se ha desactivado el firewall\n'
    CHECK_UPDATES = 'Comprobando actualizaciones\n'
    CHECK_CONNECTIONS = 'Comprobando conexiones externas\n'
    CHECK_ANTIVIRUS = 'Comprobando antivirus\n'
    ERROR_READING_EVENTS = 'Error: No se ha podido acceder al registro de eventos del sistema\n'
    EXECUTING_ACTION_RESPONSE_PO = 'Se va ha ejecutar la accion de respuesta de apagado del equipo\n'
    EXECUTING_ACTION_RESPONSE_SA = 'Se va ha ejecutar la accion de respuesta que muestra una alerta\n'
    EXECUTING_ACTION_RESPONSE_ND = 'Se va ha ejecutar la accion de respuesta que deshabilita los adaptadores de red\n'


class Logger:

    def write(self, state):
        log_file = open('C:\\Program Files\\AutoDiagnose\\autodiagnose.log', 'a')
        event = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + str(state)
        log_file.write(event)
        log_file.close()
