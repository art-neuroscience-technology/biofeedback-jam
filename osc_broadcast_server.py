import argparse
import random
import time

from datetime import datetime
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import sys, getopt


waves_names=['delta','theta','alpha','beta','gamma']


listeners = [{ 'ip' : "192.168.0.199", 'port' : 5001 }, { 'ip' : "192.168.0.199", 'port' : 5000 }, { 'ip' : "192.168.0.199", 'port' : 5000 }] 


ip = "0.0.0.0"
port = 5000

def forward_message(address: str, *args):
    for l in listeners:
        l['client'].send_message(address, args)
    

def main(argv):
  
   #generate identifier 
   identifier = uuid.uuid4()
   print(f'Created identifier {identifier}') 
   
   #initialize clients
   for l in listeners:
    l['client'] = udp_client.SimpleUDPClient(l['ip'], l['port'])

   dispatcher = dispatcher.Dispatcher()
   dispatcher.map("/muse/elements/delta_absolute", forward_message)
   dispatcher.map("/muse/elements/theta_absolute", forward_message)
   dispatcher.map("/muse/elements/alpha_absolute", forward_message)
   dispatcher.map("/muse/elements/beta_absolute", forward_message)
   dispatcher.map("/muse/elements/gamma_absolute", forward_message)

   server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
   print("Listening on port "+str(port))
   server.serve_forever()

if __name__ == "__main__":
   main(sys.argv[1:])


