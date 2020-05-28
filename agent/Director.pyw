import os
from multiprocessing.connection import Listener


address = ('localhost', 6000)
while True:
    listener = Listener(address, authkey=b'password')
    print('Inicia')
    conn = listener.accept()
    while True:
        msg = conn.recv()

        if msg == 'close':
            listener.close()
            break

        action = str(msg).split(',')[0]
        message = str(msg).split(',')[1]

        # Your execution directory
        os.system('C:\\Users\\ManuelTorresMendoza\\PycharmProjects\\agent1\\dist\\AutoDiagnoseActions.exe \"{}\" \"{}\"'.format(action, message))
