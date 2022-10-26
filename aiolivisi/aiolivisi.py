"""Code to handle the communication with Livisi Smart home controllers."""
from __future__ import annotations
from typing import Any
import uuid

from aiohttp.client import ClientSession

from .errors import (
    IncorrectIpAddressException,
    ShcUnreachableException,
    WrongCredentialException,
)

from .const import (
    AUTH_GRANT_TYPE,
    AUTH_PASSWORD,
    AUTH_USERNAME,
    AUTHENTICATION_HEADERS,
    CLASSIC_PORT,
    LOCATION,
    REQUEST_TIMEOUT,
    USERNAME,
)

ERRORS = {1: Exception}


class AioLivisi:
    """Handles the communication with the Livisi Smart Home controller."""

    instance = None

    def __init__(
        self, web_session: ClientSession = None, auth_headers: dict[str, Any] = None
    ) -> None:
        self._web_session: ClientSession = web_session
        self._auth_headers: dict[str, Any] = auth_headers
        self._token: str = ""
        self._livisi_connection_data: dict[str, str] = None

    async def async_set_token(
        self, livisi_connection_data: dict[str, str] = None
    ) -> None:
        """Set the JWT from the LIVISI Smart Home Controller."""
        access_data: dict = {}
        try:
            if self._livisi_connection_data is not None:
                self._livisi_connection_data = livisi_connection_data
            access_data = await self.async_get_jwt_token(livisi_connection_data)
            self.token = access_data["access_token"]
            self._auth_headers = {
                "authorization": f"Bearer {self.token}",
                "Content-type": "application/json",
                "Accept": "*/*",
            }
        except Exception as error:
            if len(access_data) == 0:
                raise IncorrectIpAddressException from error
            elif access_data["errorcode"] == 2009:
                raise WrongCredentialException from error
            else:
                raise ShcUnreachableException from error

    async def async_send_authorized_request(
        self,
        method,
        url: str,
        payload=None,
    ) -> dict:
        """Make a request to the Livisi Smart Home controller."""
        ip_address = self._livisi_connection_data["ip_address"]
        path = f"http://{ip_address}:{CLASSIC_PORT}/{url}"
        return await self.async_send_request(method, path, payload, self._auth_headers)

    async def async_send_unauthorized_request(
        self,
        method,
        url: str,
        headers,
        payload=None,
    ) -> dict:
        """Send a request without JWT token."""
        return await self.async_send_request(method, url, payload, headers)

    async def async_get_jwt_token(self, livisi_connection_data: dict[str, str]):
        """Send a request for getting the JWT token."""
        login_credentials = {
            AUTH_USERNAME: USERNAME,
            AUTH_PASSWORD: livisi_connection_data["password"],
            AUTH_GRANT_TYPE: "password",
        }
        headers = AUTHENTICATION_HEADERS
        self._livisi_connection_data = livisi_connection_data
        ip_address = self._livisi_connection_data["ip_address"]
        return await self.async_send_request(
            "post",
            url=f"http://{ip_address}:{CLASSIC_PORT}/auth/token",
            payload=login_credentials,
            headers=headers,
        )

    async def async_send_request(
        self, method, url: str, payload=None, headers=None
    ) -> dict:
        """Send a request to the Livisi Smart Home controller."""
        try:
            response = await self.__async_send_request(method, url, payload, headers)
            if "errorcode" in response:
                if response["errorcode"] == 2007:
                    await self.async_set_token()
            return response
        except Exception:
            return await self.__async_send_request(method, url, payload, headers)

    async def __async_send_request(
        self, method, url: str, payload=None, headers=None
    ) -> dict:
        async with self._web_session.request(
            method,
            url,
            json=payload,
            headers=headers,
            ssl=False,
            timeout=REQUEST_TIMEOUT,
        ) as res:
            data = await res.json()
            return data

    async def async_get_controller(self) -> dict[str, Any]:
        """Get Livisi Smart Home controller data."""
        return await self.async_get_controller_status()

    async def async_get_controller_status(self) -> dict[str, Any]:
        """Get Livisi Smart Home controller status."""
        shc_info = await self.async_send_authorized_request("get", url="status")
        return shc_info

    async def async_get_devices(
        self,
    ) -> list[dict[str, Any]]:
        """Send a request for getting the devices."""
        devices = await self.async_send_authorized_request("get", url="device")
        for device in devices.copy():
            if LOCATION in device and device.get(LOCATION) is not None:
                device[LOCATION] = device[LOCATION].removeprefix("/location/")
        return devices

    async def async_get_pss_state(self, capability) -> dict[str, Any] | None:
        """Get the state of the PSS device."""
        url = f"{capability}/state"
        try:
            return await self.async_send_authorized_request("get", url)
        except Exception:
            return None

    async def async_pss_set_state(self, capability_id, is_on: bool) -> dict[str, Any]:
        """Set the PSS state."""
        set_state_payload: dict[str, Any] = {
            "id": uuid.uuid4().hex,
            "type": "SetState",
            "namespace": "core.RWE",
            "target": capability_id,
            "params": {"onState": {"type": "Constant", "value": is_on}},
        }
        return await self.async_send_authorized_request(
            "post", "action", payload=set_state_payload
        )

    async def async_get_all_rooms(self) -> dict[str, Any]:
        """Get all the rooms from LIVISI configuration."""
        return await self.async_send_authorized_request("get", "location")

    @property
    def livisi_connection_data(self):
        """Return the connection data."""
        return self._livisi_connection_data

    @livisi_connection_data.setter
    def livisi_connection_data(self, new_value):
        self._livisi_connection_data = new_value

    @property
    def token(self):
        """Return the token."""
        return self._token

    @token.setter
    def token(self, new_value):
        self._token = new_value

    @property
    def web_session(self):
        """Return the web session."""
        return self._web_session

    @web_session.setter
    def web_session(self, new_value):
        self._web_session = new_value
