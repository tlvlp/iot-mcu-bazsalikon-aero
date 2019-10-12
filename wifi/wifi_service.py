import network
import uasyncio as asyncio
from unit import shared_flags, config


class WifiService(object):

    def __init__(self) -> None:
        """
        Wifi Service for the tlvlp.iot project
        Handles the connection to the WLAN network

        Tested on ESP32 MCUs
        """
        print("Wifi service - Initializing service")
        # Init values
        self.wifi_client = network.WLAN(network.STA_IF)
        self.connection_in_progress = False
        # Add scheduled tasks
        loop = asyncio.get_event_loop()
        loop.create_task(self.connection_checker_loop())
        print("Wifi service - Service initialization complete")

    async def connection_checker_loop(self) -> None:
        """ Periodically checks the connection status and reconnects if necessary """
        while True:
            if not self.wifi_client.isconnected() and not self.connection_in_progress:
                await self.connect()
            await asyncio.sleep(config.wifi_connection_check_interval_sec)

    async def connect(self) -> None:
        shared_flags.wifi_is_connected = False
        self.connection_in_progress = True
        print("Wifi service - Connecting")
        access_point = config.wifi_ssid
        password = config.wifi_password
        self.wifi_client.active(True)
        self.wifi_client.connect(access_point, password)
        while not self.wifi_client.isconnected():
            await asyncio.sleep(0)
        config.wifi_ip = self.wifi_client.ifconfig()[0]
        print("Wifi service - Connection established (access_point: {}, password: {}, ip: {})".format(
            access_point, password, config.wifi_ip))
        shared_flags.wifi_is_connected = True
        self.connection_in_progress = False

