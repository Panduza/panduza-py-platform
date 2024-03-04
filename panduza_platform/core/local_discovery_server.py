# UPD server listening for a client broadcast and responding by giving its IP and name

import asyncio
import socket
import json

class Server:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        json_message = json.loads(message)
        print('received : %r from %s' % (json_message, addr))
        
        json_reply = '{"name": "panduza_platform","version": 1.0}'
        self.transport.sendto(json_reply.encode(), addr)
        print('send : %r to %s' % (json_reply, addr))