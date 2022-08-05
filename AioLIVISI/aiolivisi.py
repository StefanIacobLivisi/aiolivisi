"""Code to handle the communication with Livisi Smart home controllers."""
from logging import Logger
from typing import Any
import uuid

from aiohttp.client import ClientSession

from .errors import IncorrectIpAddressException, ShcUnreachableException, WrongCredentialException

from .const import (
    AUTH_GRANT_TYPE,
    AUTH_PASSWORD,
    AUTH_USERNAME,
    AUTHENTICATION_HEADERS,
    CLASSIC_PORT,
    USERNAME,
)

ERRORS = {1: Exception}


class AioLivisi:
    """Handles the communication with the Livisi Smart Home controller."""

    instance = None

    def __init__(self, auth_headers: dict[str, Any] = None) -> None:
        self._auth_headers = auth_headers
        self._token: str = ""
        self._livisi_connection_data: dict[str, str] = None
        if AioLivisi.instance is not None:
            raise Exception("This class is a singleton!")
        else:
            AioLivisi.instance = self

    @staticmethod
    def get_instance():
        """Static access method."""
        if AioLivisi.instance is None:
            AioLivisi()
        return AioLivisi.instance

    async def async_set_token(
        self, web_session, livisi_connection_data: dict[str, str] = None
    ):
        """Set the JWT from the LIVISI Smart Home Controller."""
        access_data: dict = {}
        try:
            if self._livisi_connection_data is not None:
                self._livisi_connection_data = livisi_connection_data
            access_data = await self.async_get_jwt_token(
                web_session, livisi_connection_data
            )
            self.token = access_data["access_token"]
            self._auth_headers = {
                "authorization": f"Bearer {self.token}",
                "Content-type": "application/json",
                "Accept": "*/*",
            }
        except Exception as error:
            if len(access_data) == 0:
                raise IncorrectIpAddressException from error
            if access_data["errorcode"] == 2009:
                raise WrongCredentialException from error
            raise ShcUnreachableException from error

    async def async_send_authorized_request(
        self,
        method,
        web_session: ClientSession,
        url: str,
        payload=None,
    ) -> dict:
        """Make a request to the Livisi Smart Home controller."""
        ip_address = self._livisi_connection_data["ip_address"]
        path = f"http://{ip_address}:{CLASSIC_PORT}/{url}"
        return await self.async_send_request(
            method, web_session, path, payload, self._auth_headers
        )

    async def async_send_unauthorized_request(
        self,
        method,
        web_session: ClientSession,
        url: str,
        headers,
        payload=None,
    ):
        """Send a request without JWT token."""
        return await self.async_send_request(method, web_session, url, payload, headers)

    async def async_get_jwt_token(
        self, web_session, livisi_connection_data: dict[str, str]
    ):
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
            web_session,
            url=f"http://{ip_address}:{CLASSIC_PORT}/auth/token",
            payload=login_credentials,
            headers=headers,
        )

    async def async_send_request(
        self, method, web_session: ClientSession, url: str, payload=None, headers=None
    ) -> dict:
        """Send a request to the Livisi Smart Home controller."""
        try:
            response = await self.__async_send_request(
                method, web_session, url, payload, headers
            )
            if "errorcode" in response:
                if response["errorcode"] == 2007:
                    await self.async_set_token(web_session)
            return response
        except Exception:
            return await self.__async_send_request(
                method, web_session, url, payload, headers
            )

    async def __async_send_request(
        self, method, web_session: ClientSession, url: str, payload=None, headers=None
    ) -> dict:
        async with web_session.request(
            method, url, json=payload, headers=headers, ssl=False, timeout=2000
        ) as res:
            data = await res.json()
            return data

    async def async_get_controller(
        self,
        websession,
    ) -> dict[str, Any]:
        """Get Livisi Smart Home controller data."""
        return await self.async_get_controller_status(
            websession,
        )

    async def async_get_controller_status(
        self,
        websession,
    ) -> dict[str, Any]:
        """Get Livisi Smart Home controller status."""
        shc_info = await self.async_send_authorized_request(
            "get", websession, url="status"
        )
        return shc_info

    async def async_get_devices(
        self,
        websession,
    ):
        """Send a request for getting the devices."""
        return await self.async_send_authorized_request("get", websession, url="device")

    async def async_get_pss_state(self, websession, capability):
        """Get the state of the PSS device."""
        url = f"{capability}/state"
        try:
            return await self.async_send_authorized_request("get", websession, url)
        except Exception as error:
            Logger.error("There was an error getting the PSS state %s", error)
            return

    async def async_pss_set_state(self, websession, capability_id, is_on: bool):
        """Set the PSS state."""
        set_state_payload: dict[str, Any] = {
            "id": uuid.uuid4().hex,
            "type": "SetState",
            "namespace": "core.RWE",
            "target": capability_id,
            "params": {"onState": {"type": "Constant", "value": is_on}},
        }
        return await self.async_send_authorized_request(
            "post", websession, "action", payload=set_state_payload
        )

    async def async_get_all_rooms(self, websession):
        """Get all the rooms from LIVISI configuration."""

        return await self.async_send_authorized_request("get", websession, "location")

    @property
    def livisi_connection_data(self):
        """Return the log in headers"""
        return self._livisi_connection_data

    @livisi_connection_data.setter
    def livisi_connection_data(self, new_value):
        self._livisi_connection_data = new_value

    @property
    def token(self):
        """Return the log in headers"""
        return self._token

    @token.setter
    def token(self, new_value):
        self._token = new_value
