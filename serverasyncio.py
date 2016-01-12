#!/usr/bin/env python3.5

import asyncio
import logging
from settings_local import *


#FORMAT = '%(asctime)-15s %(clientip)s %(message)s'
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('./serverasyncio.log')
root_logger = logging.getLogger()
root_logger.addHandler(stream_handler)
root_logger.addHandler(file_handler)
root_logger.setLevel("INFO")

class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        msg = 'Connection from {}'.format(peername)
        root_logger.info(msg)
        self.transport = transport
        self.transport.set_write_buffer_limits(high=200000*64*1204)

    def data_received(self, data):
        message = ""
        try:
            message = data.decode()
        except Exception as e:
            root_logger.error(e)
        msg = 'Data received: {!r}'.format(message)
        root_logger.info(msg)

        msg = 'Send: {!r}'.format(message)
        root_logger.info(msg)
        fut = asyncio.async(self.sleeper(data))
        result = asyncio.wait_for(fut, 60)

        if message == "CLOSE\r\n":
            msg = 'Close the client socket'
            root_logger.error(msg)
            self.transport.close()

    async def sleeper(self, data):
        i=0
        while i<3:
            await asyncio.sleep(0.3)
            #self.transport.write("Hello World".encode())
            self.transport.write(data)
            i+=1


loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(EchoServerClientProtocol, HOST, PORT)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
root_logger.info('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

