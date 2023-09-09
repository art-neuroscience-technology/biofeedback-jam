import argparse
import random
import time
import numpy as np

from datetime import datetime
from pythonosc import dispatcher, osc_server, udp_client

touching_forehead = False


#initialize clients
listeners = [{ 'ip' : "127.0.0.1", 'port' : 5000 },
             { 'ip' : "127.0.0.1", 'port' : 5001 }] 


for l in listeners:
    l['client'] = udp_client.SimpleUDPClient(l['ip'], l['port'])
    
ip = "0.0.0.0"
port = 5002
max_time = 5
elapsed_time = 0
init_time = -1

def complete_args(original_list):
    min_value = -0.9
    max_value = 0.9
    result = [random.uniform(min_value, max_value) if value == 0.0 else value for value in original_list]
    return result

def check_touching_forehead(address: str, *args):
    global touching_forehead
    try:
        stream = (args[0]==1)
        if touching_forehead and not stream:
            print('Stop streaming')
        elif not touching_forehead and stream:
            print('Start streaming')
        touching_forehead=(args[0]==1)
    except:
        pass
    
def forward_message(address: str, *args):
    global listeners
    global touching_forehead
    global init_time
    global elapsed_time
    global max_time
    
    try:
        if touching_forehead:
            if init_time == -1:
                init_time = time.time()
            else:
                elapsed_time = time.time() - init_time
            if (elapsed_time>max_time):
                waves_values = complete_args([args[0],args[1], args[2],args[3]])
                print('waves:', waves_values)
                elapsed_time = 0
                init_time = -1
                for l in listeners:
                    l['client'].send_message(address, waves_values)
        
    except:
        pass
    
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/muse/elements/delta_absolute", forward_message)
dispatcher.map("/muse/elements/theta_absolute", forward_message)
dispatcher.map("/muse/elements/alpha_absolute", forward_message)
dispatcher.map("/muse/elements/beta_absolute", forward_message)
dispatcher.map("/muse/elements/gamma_absolute", forward_message)
dispatcher.map("/muse/elements/touching_forehead", check_touching_forehead)

server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
print("Listening on port "+str(port))
server.serve_forever()

