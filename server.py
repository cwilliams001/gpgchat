"""
server
Message transport server.
"""

import re
import zmq
import argparse
import importlib.util

def load_config(path):
    spec = importlib.util.spec_from_file_location("config", path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

class Server(object):
  def __init__(self, config):
    self.config = config
    self.context = zmq.Context()
    self.sock = self.context.socket(zmq.REP)
    self.sock.bind('tcp://*:{}'.format(self.config.SERVER_PORT))
    print("Server listening on port {}".format(self.config.SERVER_PORT))

    self.messages = []

  def listen(self):
    while True:
      msg = self.sock.recv()
      mtype_match = re.match(b"(.*)\n", msg)
      if not mtype_match:
          continue
      mtype = mtype_match.groups(1)[0]
      if mtype == b"send":
        self._receive_message(msg[len("send\n"):])
        self.sock.send(b"OK")
      elif mtype == b"fetchmessage":
        index_match = re.match(b".*\n(.*)", msg)
        if not index_match:
            continue
        index = index_match.groups(1)[0]
        index = int(index)
        self.sock.send(self._fetch_message(index))
      else:
        print("Unrecognized message type: {}".format(mtype))

  def _receive_message(self, msg):
    print("Message received.")
    print('\n'.join([">> " + line for line in msg.decode('utf-8').split('\n')]))
    self.messages.append(msg)

  def _fetch_message(self, index):
    print("Client asked for message {}".format(index))
    if index < len(self.messages):
      print("  responding with message.")
      return self.messages[index]
    else:
      print("  responding NOMESSAGE.")
      return b"NOMESSAGE"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.py', help='Path to the configuration file.')
    args = parser.parse_args()

    config = load_config(args.config)
    
    s = Server(config)
    s.listen()
