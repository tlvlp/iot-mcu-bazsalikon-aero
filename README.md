# IoT MCU - BazsalikOn Aero

## Summary
- Part of the [tlvlp IoT project](https://github.com/tlvlp/iot-project-summary)
- Implements the MCU side API of the services that is documented at the [iot-mcu-modules](https://github.com/tlvlp/iot-mcu-modules)
- Template for the project can be found at the [iot-mcu-modules](https://github.com/tlvlp/iot-mcu-modules)

This specific implementation runs on an ESP32 microcontroller that monitors and controls the aeroponic grow section of my indoor garden.

## Usage
Upload helper scrips can be found at [micropython-upload](https://github.com/tlvlp/micropython-upload) but they still need some manual configuration.
1. Update the ESP32 module to the latest [MicroPython](http://micropython.org/download#esp32) firmware.
2. Clone this repository
3. Fill the placeholder values in the [config.py](unit/config.py)
4. Upload the contents to the MCU with eg. [ampy](https://github.com/scientifichackers/ampy) that is also used by the above scripts.
5. Make sure that the MQTT broker that is part of the tlvlp IoT project is running.
6. Test the unit with either via the project or via any third party MQTT client by subscribing and posting to theAPI topics.
7. The unit is ready to be installed.