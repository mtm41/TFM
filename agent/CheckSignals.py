import datetime
import json
import subprocess
import sys
import time

import requests


class CheckIsUp:

    # This method will send signals periodically to the external agent for the purpose of
    # controlling deliberately desactivation
    def sendSignal(self, api_endpoint, key, state):
        data = {'key': key, 'state': state}
        failed = False
        while not failed:
            started = datetime.datetime.now()
            sendSignalTime = datetime.datetime.now()
            rest = (started.minute + 30) % 60
            if (started.minute + 30) / 60 >= 1:
                sendSignalTime = sendSignalTime.replace(hour=sendSignalTime.hour + 1)
            sendSignalTime = sendSignalTime.replace(minute=rest)

            print(datetime.datetime.now())
            print(sendSignalTime)
            while datetime.datetime.now() <= sendSignalTime:
                print('Entra')
                try:
                    configFile = 'C:\\tracker.log'
                    f = open(configFile, 'w')
                    f.write('Ejecuto')
                    cmd = 'net start | find /i "Agent Monitor"'
                    out = subprocess.check_output(cmd, shell=True)
                    f.close()
                    time.sleep(240)
                except Exception as ex:
                    print(ex)
                    data['state'] = 'end'
                    resp = requests.post(url=api_endpoint, verify=False, data=data)  # Send stop signal
                    failed = True
                    break

            if not failed:
                resp = requests.put(url=api_endpoint, verify=False, data=data)  # Send update signal


if __name__ == "__main__":
    check = CheckIsUp()
    check.sendSignal(sys.argv[1], sys.argv[2], sys.argv[3])
