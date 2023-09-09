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
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5002,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

`'''The absolute band power for a given frequency range
(for instance, alpha, i.e. 9-13Hz) is the logarithm of the sum
of the Power Spectral Density of the EEG data over that frequency range.
They are provided for each of the four to six channels/electrode sites on Muse.
Since it is a logarithm, some of the values will be negative
(i.e. when the absolute power is less than 1)
They are given on a log scale, units are Bels.'''
while(True):
  for waves_name in waves_names:
    client.send_message(f"/muse/elements/{waves_name}_absolute", 
      [random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9),random.uniform(-0.9, 0.9)])
  time.sleep(1)

