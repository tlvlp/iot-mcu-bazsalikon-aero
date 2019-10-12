from wifi.wifi_service import WifiService
from mqtt.mqtt_service import MqttService
from unit.unit_service import UnitService
from unit import config
import uasyncio as asyncio
import gc
import machine


def main() -> None:
    """ Main module of the tlvlp.iot project """

    # Init services
    WifiService()
    mqtt_service = MqttService()
    UnitService(mqtt_service)

    # Start all scheduled co-routines
    loop = asyncio.get_event_loop()
    loop.create_task(garbage_collector_loop())
    try:
        loop.run_forever()
    except IndexError:
        # Reset the unit if the task loop runs out of coros and freezes eg in a message flood.
        machine.reset()


async def garbage_collector_loop():
    """ Periodically runs the garbage collection """
    while True:
        print("Running garbage collection")
        gc.collect()
        await asyncio.sleep(config.gc_collect_interval_sec)


if __name__ == '__main__':
    main()

