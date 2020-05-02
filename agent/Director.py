import os
from multiprocessing.connection import Listener


address = ('localhost', 6000)
while True:
    listener = Listener(address, authkey=b'password')
    print('Inicia')
    conn = listener.accept()
    while True:
        print('Otra')
        msg = conn.recv()

        if msg == 'close':
            listener.close()
            break

        print(msg)
        action = str(msg).split(',')[0]
        message = str(msg).split(',')[1]

        os.system('python C:\\Users\\ManuelTorresMendoza\\PycharmProjects\\agent1\\ActionResponse.py \"{}\" \"{}\"'.format(action, message))
