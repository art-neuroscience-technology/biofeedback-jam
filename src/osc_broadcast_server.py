import argparse
import random
import time

from datetime import datetime
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client



#initialize clients
listeners = [{ 'ip' : "127.0.0.1", 'port' : 5002 },
             { 'ip' : "127.0.0.1", 'port' : 5001 }] 


for l in listeners:
    l['client'] = udp_client.SimpleUDPClient(l['ip'], l['port'])
    
ip = "0.0.0.0"
port = 5000

def forward_message(address: str, *args):
    global listeners
    
    try:
        print(address, args)
        for l in listeners:
            l['client'].send_message(address, args)
    except:
        pass
    
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/muse/elements/delta_absolute", forward_message)
dispatcher.map("/muse/elements/theta_absolute", forward_message)
dispatcher.map("/muse/elements/alpha_absolute", forward_message)
dispatcher.map("/muse/elements/beta_absolute", forward_message)
dispatcher.map("/muse/elements/gamma_absolute", forward_message)

server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
print("Listening on port "+str(port))
server.serve_forever()

