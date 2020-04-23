from datetime import datetime

from DatabaseConnection import DatabaseConnection
import calendar;
import time;

class Watcher:

    def __init__(self):
        self.date = datetime.now()
        self.con = DatabaseConnection(False).conn

    def save_report(self, report):
        reportLocation = 'C:\\autoDiagnose_{}.json'.format(calendar.timegm(time.gmtime()))
        sql = "INSERT INTO Informe VALUES (?,?,?)"

        data_tuple = (calendar.timegm(time.gmtime()), datetime.now(), 'JSON')
        cur = self.con.cursor()
        cur.execute(sql, data_tuple)

        f = open(reportLocation, 'w')
        htmlReport = '<html><head><title>Informe</title><style type="text/css">' \
                     '.test-result-table{border: 1px solid black;width: 800px;}' \
                     '.test-result-table-header-cell{border-bottom: 1px solid black;background-color: silver;}' \
                     '.test-result-step-command-cell{border-bottom: 1px solid gray;}' \
                     '.test-result-step-description-cell {border-bottom: 1px solid gray;}' \
                     '.test-result-step-result-cell-ok {border-bottom: 1px solid gray;background-color: white;}' \
                     '.test-result-step-result-cell-failure {border-bottom: 1px solid gray;background-color: red;}' \
                     '.test-result-step-result-cell-notperformed {border-bottom: 1px solid gray;background-color: white;}' \
                     '.test-result-describe-cell {background-color: tan;font-style: italic;}' \
                     '.test-cast-status-box-ok{border: 1px solid black;float: left;margin-right: 10px;width: 45px;height: 25px;background-color: green;}' \
                     '</style></head><body><h1 class="test-results-header">Informe</h1>' \
                     '<table class="test-result-table" cellspacing="0"><thead><tr>' \
                     '<td class="test-result-table-header-cell">Incidente</td>' \
                     '<td class="test-result-table-header-cell">Fecha</td><td class="test-result-table-header-cell">Evento</td>' \
                     '<td class="test-result-table-header-cell">Criticidad</td>'

        replaceString = '</tr></thead><tbody>{}</tbody></table></body></html>'

        incidentStructure = '<tr class="test-result-step-row test-result-step-row-altone"><td class="test-result-step-command-cell">{}' \
                            '</td><td class="test-result-step-description-cell">{}</td>' \
                            '<td class="test-result-step-result-cell-ok">{}</td>' \
                            '<td class="test-result-step-result-cell-ok">{}</td></tr>'

        translation = {
            'ExternalDeviceConnection': 'Dispositivos externo conectado',
            'NewInstallationDetection': 'Instalaciones detectadas',
            'NewInstallation': 'Instalacion segura detectada',
            'NewInstallationFromKnownEditor': 'Instalacion de un editor desconocido detectada',
            'NewInstallationFromOwnInstaller': 'Instalacion, mediante un instalador propio, detectada',
            'AntivirusNotInstalled': 'No se ha detectado ningún antivirus instalado',
            'AntivirusInstalledWithoutVersion': 'Se ha detectado antivirus, pero no se ha detectado la versión',
            'AntivirusNotPresent': 'Se ha detectado antivirus instalado, pero el servicio no se está ejecutando',
            'AntivirusNotUpToDate': 'El antivirus no está actualizado',
            'UpdateFailed': 'Una actualización del sistema ha fallado',
            'UpdatesNotEnabled': 'Las actualizaciones automáticas han sido desactivadas',
            'LastUpdate': 'Actualización del sistema instalada',
            'FirewallNotEnabled': 'El servicio firewall se encuentra desactivado',
            'FirewallDisabledByUser': 'Firewall desactivado por el usuario',
            'DgaConnection': 'Conexión externa detectada como DGA',
            'ExternalConnection': 'Conexión externa'
        }

        eventStructure = ''
        for incident in report.keys():
            if report[incident]:
                incidentTranslate = translation[incident]
                for event in report[incident]:
                    date = event[0]
                    details = event[1]
                    mark = event[2]
                    eventStructure += incidentStructure.format(incidentTranslate, date, details, mark)
        print('\n')
        htmlReport += replaceString.format(eventStructure)

        f.write(htmlReport)
        f.close()



    def send_report(self):
        incidents = [
            'ExternalDeviceConnection',
            'NewInstallationDetection',
            'NewInstallation',
            'NewInstallationFromKnownEditor',
            'NewInstallationFromOwnInstaller',
            'AntivirusNotInstalled',
            'AntivirusInstalledWithoutVersion',
            'AntivirusNotPresent',
            'AntivirusNotUpToDate',
            'UpdateFailed',
            'UpdatesNotEnabled',
            'LastUpdate',
            'FirewallNotEnabled',
            'FirewallDisabledByUser',
            'DgaConnection'
        ]
        report = {}
        for incident in incidents:
            sql = "SELECT DISTINCT evento.fecha, evento.detalles, criticidad FROM evento,incidente WHERE evento.incidente LIKE '%{}%' " \
                  "AND strftime('%s', '{}') - strftime('%s',fecha) < 0 AND evento.incidente=incidente.nombre"\
                .format(incident, str(datetime.today().strftime("%Y-%m-%d 00:00:00")))

            events = []

            cur = self.con.cursor()
            print(sql)
            cur.execute(sql)
            resultSet = cur.fetchall()

            numberOfEvents = len(resultSet)
            print(numberOfEvents)
            for row in resultSet:
                events.append(row)

            report[incident] = []
            for event in events:
                report[incident].append(event)

        sql = "SELECT ip, dominio, fecha FROM DgaDomain WHERE strftime('%s', '{}') - strftime('%s',fecha) < 0 AND dga=0"\
            .format(str(datetime.today().strftime("%Y-%m-%d 00:00:00")))
        cur = self.con.cursor()
        cur.execute(sql)
        resultSet = cur.fetchall()
        print(len(resultSet))
        report['ExternalConnection'] = []
        for row in resultSet:
            data_tuple = (row[2], 'Ip: {}. Dominio: {}'.format(row[0], row[1]), '2')
            report['ExternalConnection'].append(data_tuple)

        print(report)
        self.save_report(report)
            #sql = "INSERT INTO Informe VALUES (?,?,?)"
        self.con.close()


if __name__ == "__main__":
    watcher = Watcher()
    watcher.send_report()