import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

_connections = {}


def connect(host='localhost', port=27017, io_loop=asyncio.get_event_loop()):
    if (host, port) not in _connections:
        _connections[host, port] = AsyncIOMotorClient(host=host, port=port, io_loop=io_loop)
    return _connections[host, port]
