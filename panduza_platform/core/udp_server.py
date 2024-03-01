# UPD server listening for a client broadcast and responding by giving its IP and name

import asyncio
import socket

class Server:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('received : %r from %s' % (message, addr))
        
        hostname = socket.gethostname()
        IP_addr = socket.gethostbyname(hostname)
        reply = "Yes! I am server %s and my address is %s" % (hostname, IP_addr)
        self.transport.sendto(reply.encode(), addr)
        print('send : %r to %s' % (reply, addr))