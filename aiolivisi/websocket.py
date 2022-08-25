"""Code for communication with the Livisi application websocket."""
from typing import Callable
import urllib.parse

import websockets
from pydantic import ValidationError

from aiolivisi.event_data import EventData

from .aiolivisi import AioLivisi
from .const import AVATAR_PORT


class Websocket:
    """Represents the websocket class."""

    instance = None

    def __init__(self) -> None:
        """Initialize the websocket."""
        self.aiolivisi = AioLivisi.get_instance()
        self.connection_url: str = None
        self._websocket = None

    @staticmethod
    def get_instance():
        """Static access method."""
        if Websocket.instance is None:
            Websocket()
        return Websocket.instance

    async def connect(self, on_data, on_close, port) -> None:
        """Connect to the socket."""
        if port == AVATAR_PORT:
            token = urllib.parse.quote(self.aiolivisi.token)
        else:
            token = self.aiolivisi.token
        ip_address = self.aiolivisi.livisi_connection_data["ip_address"]
        self.connection_url = f"ws://{ip_address}:{port}/events?token={token}"
        try:
            async with websockets.connect(
                self.connection_url, ping_interval=10, ping_timeout=10
            ) as websocket:
                try:
                    self._websocket = websocket
                    await self.consumer_handler(websocket, on_data)
                except Exception:
                    await on_close()
                    return
        except Exception:
            await on_close()
            return

    async def disconnect(self) -> None:
        """Close the websocket."""
        await self._websocket.close(code=1000, reason="Handle disconnect request")

    async def consumer_handler(self, websocket, on_data: Callable):
        """Used when data is transmited using the websocket."""
        try:
            async for message in websocket:
                event_data = EventData.parse_raw(message)
                on_data(event_data)
        except ValidationError:
            on_data() 
