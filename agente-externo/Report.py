from datetime import datetime

from Model.Organization import Organization
from Model.Service import Service
from Model.Test import Test


class Report:
    def __init__(self, timestamp, organization):
        self.datetime = datetime.strptime(timestamp, '%y%m%d')
        self.organization = organization

    def generate(self):
        org_model = Organization(self.organization)
        org_model = org_model.read()

        organization_report = {
            "Organization": self.organization,
            "Report Date": str(self.datetime),
            "Phone Number": org_model.tel,
            "AdminEmail": org_model.email,
            "Services": []
        }

        services = Service(self.organization).readByOrganization()

        for service in services:
            service_report = {
                "IP": service.ip,
                "Port": service.port,
                "Technology": service.technology,
                "Analysis Time": str(service.analysisTime)[-8:],
                "Tests": []
            }

            tests = Test(service.ip, service.port, service.organization).read(self.datetime)

            for test in tests:
                test_report = {
                    "Name": test.name,
                    "Type": test.type,
                    "Analysised Time": str(test.analysisTime),
                    "Analysis End Time": str(test.endDate),
                    "State": test.state,
                    "Description": test.description,
                    "Advice": test.advice
                }
                service_report["Tests"].append(test_report)

            organization_report["Services"].append(service_report)

        return organization_report
