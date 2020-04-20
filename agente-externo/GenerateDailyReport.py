import sys
from datetime import datetime

import requests

import server
from Model.Organization import Organization


class GenerateDailyReport:

    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def generate(self):
        date = str(self.year + self.month + self.day)
        org = Organization()
        api_endpoint = 'http://192.168.1.127:5000/api/{}/report/{}'
        for (api_key, email) in org.readOrgWithService():
            api_endpoint = api_endpoint.format(api_key, date)
            resp = requests.get(url=api_endpoint, verify=False)
            response = resp.json()
            report = self.generateHtml(response)
            server.sendReportToUser(email, report, 'Publica')

    def generateHtml(self, jsonReport):
        reportTitle1 = '<h1 class="test-results-header">Informe {} / Dia {}</h1>'.format(jsonReport['Organization'],
                                                                                        jsonReport['Report Date'])
        reportTitle2 = '<h2 class="test-results-header">IP: {} Puerto: {} Tecnologia: {}</h2>'

        htmlReport_header = '<html><head><title>Informe Servicios publicos</title><style type="text/css">' \
                            '.test-result-table{border: 1px solid black;width: 800px;}' \
                            '.test-result-table-header-cell{border-bottom: 1px solid black;background-color: silver;}' \
                            '.test-result-step-command-cell{border-bottom: 1px solid gray;}' \
                            '.test-result-step-description-cell {border-bottom: 1px solid gray;}' \
                            '.test-result-step-result-cell-ok {border-bottom: 1px solid gray;background-color: white;}' \
                            '.test-result-step-result-cell-failure {border-bottom: 1px solid gray;background-color: red;}' \
                            '.test-result-step-result-cell-notperformed {border-bottom: 1px solid gray;background-color: white;}' \
                            '.test-result-describe-cell {background-color: tan;font-style: italic;}' \
                            '.test-cast-status-box-ok{border: 1px solid black;float: left;margin-right: 10px;width: 45px;height: 25px;background-color: green;}' \
                            '</style></head><body>'

        htmlReport_body = '<table class="test-result-table" cellspacing="0"><thead><tr>' \
                          '<td class="test-result-table-header-cell">Nombre</td>' \
                          '<td class="test-result-table-header-cell">Tipo</td>' \
                          '<td class="test-result-table-header-cell">Fecha Inicio</td>' \
                          '<td class="test-result-table-header-cell">Fecha Fin</td>' \
                          '<td class="test-result-table-header-cell">Estado</td>' \
                          '<td class="test-result-table-header-cell">Descripcion</td>'

        testStructure = '<tr class="test-result-step-row test-result-step-row-altone">' \
                        '<td class="test-result-step-command-cell">{}' \
                        '</td><td class="test-result-step-description-cell">{}</td>' \
                        '<td class="test-result-step-result-cell-ok">{}</td>' \
                        '<td class="test-result-step-result-cell-ok">{}</td>' \
                        '<td class="test-result-step-result-cell-ok">{}</td>' \
                        '<td class="test-result-step-result-cell-ok">{}</td></tr>'

        replaceString = '</tr></thead><tbody>{}</tbody></table></body></html>'

        services = jsonReport['Services']
        htmlReport = ''
        service_header = ''
        serviceBody = ''
        for service in services:
            service_header = reportTitle2.format(service['IP'], service['Port'], service['Technology'])
            tests = service['Tests']

            serviceBody = htmlReport_body
            for test in tests:
                serviceBody += testStructure.format(test['Name'], test['Type'], test['Analysised Time'],
                                                    test['Analysis End Time'], test['State'], test['Description'])

            htmlReport += service_header + replaceString.format(serviceBody)

        return htmlReport_header + reportTitle1 + htmlReport



if __name__ == '__main__':
    gen = GenerateDailyReport(sys.argv[1], sys.argv[2], sys.argv[3])
    gen.generate()
