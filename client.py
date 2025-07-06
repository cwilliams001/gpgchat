"""
GPG Chat Client
"""

import time
import zmq
import gpgio
import threading
import sys
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
import importlib.util

def load_config(path):
    spec = importlib.util.spec_from_file_location("config", path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

class ChatClient(object):
    def __init__(self, session, config):
        self.session = session
        self.config = config
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REQ)
        dest = "tcp://{}:{}".format(self.config.SERVER_HOSTNAME, self.config.SERVER_PORT)
        self.sock.connect(dest)
        self.last_message_index = -1
        self.running = True

    def fetch_message(self, index):
        packet = "fetchmessage\n{}".format(index)
        self.sock.send(packet.encode('utf-8'))
        response = self.sock.recv()
        if response == b"NOMESSAGE":
            return None
        else:
            return response

    def fetch_messages_since(self, last_index):
        new_messages = []
        msg = self.fetch_message(last_index + 1)
        while msg != None:
            last_index += 1
            new_messages.append((last_index, msg))
            msg = self.fetch_message(last_index + 1)
        return new_messages

    def send_message(self, msg):
        packet = "send\n{}".format(msg)
        self.sock.send(packet.encode('utf-8'))
        response = self.sock.recv()
        if response != b"OK":
            raise RuntimeError("Message send failed.")

    def listen(self):
        while self.running:
            time.sleep(1)
            new_messages = self.fetch_messages_since(self.last_message_index)
            for (index, message) in new_messages:
                try:
                    decrypted_message = gpgio.decrypt(message)
                    self.session.print_text(f"\n{decrypted_message}\n------------------------------\n")
                except gpgio.DecryptionError:
                    self.session.print_text("\nERROR: Failed to decrypt message.\n------------------------------\n")
                self.last_message_index = index

    def talk(self):
        keys = gpgio.gpg.list_keys()
        signer_name = ""
        for key in keys:
            if key['fingerprint'] == self.config.SIGNER_FINGERPRINT:
                signer_name = key['uids'][0]
                break

        bottom_toolbar = HTML(f'Logged in as: <b>{signer_name}</b> (Ctrl+D or Ctrl+C to exit)')

        while True:
            try:
                msg_cleartext = self.session.prompt(
                    '> ',
                    multiline=True,
                    bottom_toolbar=bottom_toolbar,
                    prompt_continuation='  '
                )
                
                if not msg_cleartext.strip():
                    continue

                crypt = gpgio.gpg.encrypt(
                    msg_cleartext,
                    self.config.RECIPIENTS,
                    sign=self.config.SIGNER_FINGERPRINT
                )

                if not crypt:
                    self.session.print_text("Error encrypting message.")
                    continue

                self.send_message(str(crypt))

            except (EOFError, KeyboardInterrupt):
                break
        
        self.running = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.py', help='Path to the configuration file.')
    args = parser.parse_args()

    config = load_config(args.config)
    
    session = PromptSession()
    client = ChatClient(session, config)
    
    listener_thread = threading.Thread(target=client.listen)
    listener_thread.daemon = True
    listener_thread.start()
    
    client.talk()
