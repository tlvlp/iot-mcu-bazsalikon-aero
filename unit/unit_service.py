import uasyncio as asyncio
import ujson
from unit import config, shared_flags
from modules.relay import Relay
from modules.temp_sensor_ds18b20 import TempSensorDS18B20
from modules.exceptions import InvalidModuleInputException
from mqtt.mqtt_service import MqttMessage


class UnitService:

    def __init__(self, mqtt_service) -> None:
        """
        Unit Service for the tlvlp.iot project
        Handles all unit related events and information

        Tested on ESP32 MCUs
        :param mqtt_service: tlvlp.iot mqtt service instance
        """
        print("Unit service - Initializing service")
        self.mqtt_service = mqtt_service
        # Init hardware
        self.water_temp_sensor = TempSensorDS18B20("waterTemperatureCelsius", config.water_temp_sensor_pin)
        self.growlight_relay = Relay("growlight",
                                     config.growlight_pin,
                                     config.growlight_relay_active_at,
                                     config.growlight_persistence_path)
        self.irrigation_relay = Relay("irrigation",
                                      config.irrigation_pin,
                                      config.irrigation_relay_active_at)
        # Run scheduled tasks
        loop = asyncio.get_event_loop()
        loop.create_task(self.automated_irrigation_loop())
        loop.create_task(self.status_updater_loop())
        loop.create_task(self.incoming_message_processing_loop())
        print("Unit service - Service initialization complete")

    async def send_status_to_server(self) -> None:
        while not shared_flags.wifi_is_connected and not shared_flags.mqtt_is_connected:
            await asyncio.sleep(0)
        status_dict = config.unit_id_dict.copy()
        status_dict.update([
            await self.water_temp_sensor.read_first_celsius(),
            self.growlight_relay.get_state(),
            self.irrigation_relay.get_state(),
            ("irrigationOnSec", config.irrigation_on_sec),
            ("irrigationOffSec", config.irrigation_off_sec)
        ])
        status_json = ujson.dumps(status_dict)
        message = MqttMessage(config.mqtt_topic_status, status_json)
        await self.mqtt_service.add_outgoing_message_to_queue(message)

    async def status_updater_loop(self) -> None:
        """ Periodically sends a status update to the server """
        while True:
            await self.send_status_to_server()
            await asyncio.sleep(config.post_status_interval_sec)

    async def incoming_message_processing_loop(self) -> None:
        """ Processes the incoming message queue"""
        while True:
            message = await self.mqtt_service.message_queue_incoming.get()
            topic = message.get_topic()
            payload = message.get_payload()
            print("Unit service - Message received from topic:{} with payload: {}".format(topic, payload))
            if topic == config.mqtt_topic_status_request:
                await self.send_status_to_server()
            elif topic == config.mqtt_topic_control:
                await self.handle_control_event(payload)
                await asyncio.sleep(0)
                await self.send_status_to_server()
            else:
                await self.send_error_to_server("Unit service - Error! Unrecognized topic: {}".format(topic))

    async def handle_control_event(self, payload_json: str) -> None:
        """ Processes an incoming control message """
        try:
            payload = ujson.loads(payload_json)
            if payload is None:
                await self.send_error_to_server("Unit service - Error parsing payload!")
            module = payload.keys()[0]
            value = payload.get(module)
            if self.growlight_relay.id in payload.keys():
                self.growlight_relay.handle_control_message(value)
            else:
                await self.send_error_to_server("Unit service - Error! Unrecognized module id: {}".format(payload_json))
        except ValueError:
            await self.send_error_to_server("Unit service - Error! Invalid payload: {}".format(payload_json))
        except InvalidModuleInputException:
            await self.send_error_to_server(
                "Unit service - Error! Invalid value in control payload: {}".format(payload_json))

    async def send_error_to_server(self, error: str) -> None:
        while not shared_flags.wifi_is_connected and not shared_flags.mqtt_is_connected:
            await asyncio.sleep(0)
        error_dict = config.unit_id_dict.copy()
        error_dict.update({
            "error": error
        })
        error_json = ujson.dumps(error_dict)
        message = MqttMessage(config.mqtt_topic_error, error_json)
        await self.mqtt_service.add_outgoing_message_to_queue(message)
        print(error)

    async def automated_irrigation_loop(self) -> None:
        """ Automatically turns the unit's irrigation on and off using pre-configured values """
        while True:
            self.irrigation_relay.relay_on()
            await asyncio.sleep(config.irrigation_on_sec)
            self.irrigation_relay.relay_off()
            await asyncio.sleep(config.irrigation_off_sec)

























