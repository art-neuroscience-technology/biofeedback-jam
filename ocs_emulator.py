"""OSC client

This program sends random values between -0.9 and 0.9 to the /waves addresses,
waiting for 1 seconds between each value.

"""
import argparse
import random
import time

from pythonosc import udp_client

waves_names=['delta','theta','alpha','beta','gamma']

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="0.0.0.0",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5000,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

while(True):
  for waves_name in waves_names:
    client.send_message(f"/muse/elements/{waves_name}_absolute", 
      [random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9),random.uniform(-0.9, 0.9)])
  time.sleep(1)

