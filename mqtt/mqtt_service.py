from umqtt.simple import MQTTClient
from uasyncio.queues import Queue
import uasyncio as asyncio
import machine
from unit import shared_flags, config


class MqttMessage:

    def __init__(self, topic: str, payload: str) -> None:
        """
        Queue items for both incoming and outgoing MQTT messages
        :param topic: MQTT topic where the payload was received from / should be delivered to
        :param payload: MQTT message payload
        """
        self.queue_item = (topic, payload)

    def get_topic(self) -> str:
        return self.queue_item[0]

    def get_payload(self) -> str:
        return self.queue_item[1]


class MqttService:

    def __init__(self) -> None:
        """
        MQTT Service for the tlvlp.iot project
        Handles the connection and communication with the server via an MQTT broker

        Currently it is using a blocking MQTT client with asynchronous co-routines. This results in blocking all the
        other coros for the duration of the connection (usually around 2-3s and the timeout is 15s)

        Tested on ESP32 MCUs
        """

        print("MQTT service - Initializing service")
        self.mqtt_client = None
        self.connection_in_progress = False
        self.message_queue_incoming = Queue(config.mqtt_queue_size)
        self.message_queue_outgoing = Queue(config.mqtt_queue_size)
        # Add scheduled tasks
        loop = asyncio.get_event_loop()
        loop.create_task(self.connection_checker_loop())
        loop.create_task(self.incoming_message_checker_loop())
        loop.create_task(self.outgoing_message_sender_loop())
        print("MQTT service - Service initialization complete")

    async def start_service(self) -> None:
        print("MQTT service - Starting service")
        self.connection_in_progress = True
        await self.init_client()
        await self.set_callback()
        await self.set_last_will()
        await self.connect_to_broker()
        await self.subscribe_to_topics()
        shared_flags.mqtt_is_connected = True
        self.connection_in_progress = False
        print("MQTT service - Service is running")

    # Startup methods

    async def init_client(self) -> None:
        print("MQTT service - Initializing client")
        self.mqtt_client = MQTTClient(config.mqtt_unit_id, config.mqtt_server, config.mqtt_port,
                                      config.mqtt_user, config.mqtt_password,
                                      ssl=config.mqtt_use_ssl, keepalive=config.mqtt_keepalive_sec)
        await asyncio.sleep(0)

    async def set_callback(self) -> None:
        print("MQTT service - Setting callback")
        self.mqtt_client.set_callback(self.callback)
        await asyncio.sleep(0)

    def callback(self, topic_bytes: bytes, payload_bytes: bytes) -> None:
        """ All incoming messages are handled by this method """
        message = MqttMessage(topic_bytes.decode(), payload_bytes.decode())
        asyncio.get_event_loop().create_task(self.add_incoming_message_to_queue(message))

    async def set_last_will(self) -> None:
        print("MQTT service - Setting last will")
        self.mqtt_client.set_last_will(config.mqtt_topic_inactive, config.mqtt_checkout_payload, qos=config.mqtt_qos)
        await asyncio.sleep(0)

    async def connect_to_broker(self) -> None:
        print("MQTT service - Connecting to broker")
        connected = False
        while not connected:
            try:
                self.mqtt_client.connect()
                connected = True
                print("MQTT service - Connected to broker")
            except OSError:
                if not shared_flags.wifi_is_connected:
                    # If the network connection is lost while trying to connect to the broker
                    machine.reset()
                await asyncio.sleep(0)
        await asyncio.sleep(0)

    async def subscribe_to_topics(self) -> None:
        print("MQTT service - Subscribing to topics")
        for topic in config.mqtt_subscribe_topics:
            self.mqtt_client.subscribe(topic, qos=config.mqtt_qos)
        await asyncio.sleep(0)

    # Interface methods

    async def add_incoming_message_to_queue(self, message: MqttMessage) -> None:
        """ Takes an MqttMessage and adds it to the queue to be processed """
        if self.message_queue_incoming.full():
            return  # filter out message flood
        await self.message_queue_incoming.put(message)

    async def add_outgoing_message_to_queue(self, message: MqttMessage) -> None:
        """ Takes an MqttMessage and adds it to the queue to be processed """
        if self.message_queue_outgoing.full():
            return  # prevent message flood
        await self.message_queue_outgoing.put(message)

    # Scheduled loops

    async def connection_checker_loop(self) -> None:
        """ Periodically checks the connection status and reconnects if necessary """
        while True:
            if not shared_flags.mqtt_is_connected and not self.connection_in_progress and shared_flags.wifi_is_connected:
                await self.start_service()
            await asyncio.sleep(config.mqtt_connection_check_interval_sec)

    async def outgoing_message_sender_loop(self) -> None:
        """ Processes the outgoing message queue"""
        while True:
            message = await self.message_queue_outgoing.get()
            topic = message.get_topic()
            payload = message.get_payload()
            try:
                while not shared_flags.mqtt_is_connected:
                    await asyncio.sleep(0)
                self.mqtt_client.publish(topic, payload, qos=config.mqtt_qos)
                print("MQTT service - Message published to topic:{} with payload: {}".format(topic, payload))
            except OSError:
                print("MQTT service - Error in publishing message to topic:{} with payload: {}".format(topic, payload))
                shared_flags.mqtt_is_connected = False

    async def incoming_message_checker_loop(self) -> None:
        """ Periodically checks for new messages at the broker. Messages will be handled via the callback method """
        while True:
            if shared_flags.mqtt_is_connected:
                try:
                    self.mqtt_client.check_msg()
                except OSError:
                    print("MQTT service - Error! Messages cannot be retrieved from the MQTT broker. Connection lost.")
                    shared_flags.mqtt_is_connected = False
            await asyncio.sleep_ms(config.mqtt_message_check_interval_ms)


