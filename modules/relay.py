from machine import Pin
from modules.exceptions import InvalidModuleInputException


class Relay:

    def __init__(self, name: str, pin_num: int, active_at: int, persist_path=None) -> None:
        """
        Relay control for the tlvlp.iot project

        Tested on ESP32 MCUs
        :param pin_num: digital output pin to control the relay
        :param active_at: the relay is either active at a HIGH(1) or LOW(0) Pin state
        :param persist_path: if a path is provided the relay's state will be persisted to and loaded from there.
        """
        reference = "relay|"
        self.id = reference + name
        self.active_at = active_at
        self.persist_path = persist_path
        self.pin = Pin(pin_num, Pin.OUT, value=self.get_off_state())
        self.state = 0
        if persist_path is None:
            self.state_is_persisted = False
            self.relay_off()
        else:
            self.state_is_persisted = True
            self.load_state_from_file()

    def get_off_state(self) -> int:
        if self.active_at == 0:
            return 1
        else:
            return 0

    def get_module_id(self) -> str:
        return self.id

    def handle_control_message(self, value: int):
        if value == 1:
            self.relay_on()
        elif value == 0:
            self.relay_off()
        else:
            raise InvalidModuleInputException

    def get_state(self) -> tuple:
        """ Returns a tuple with the reference name and the current relay state that is either 1 (on) or 0 (off) """
        return self.id, self.state

    def set_state(self, state: int):
        if int(state) == 1:
            self.relay_on()
        elif int(state) == 0:
            self.relay_off()
        else:
            error = "Relay - Error! Unrecognized relay state:" + str(state)
            print(error)
            raise ValueError(error)

    def relay_on(self) -> None:
        """ Switches the relay on """
        if self.active_at == 1:
            self.pin.on()
        else:
            self.pin.off()
        self.state = 1
        if self.state_is_persisted:
            self.save_state_to_file()

    def relay_off(self) -> None:
        """ Switches the relay off """
        if self.active_at == 1:
            self.pin.off()
        else:
            self.pin.on()
        self.state = 0
        if self.state_is_persisted:
            self.save_state_to_file()

    def load_state_from_file(self) -> None:
        try:
            with open(self.persist_path) as stateFile:
                loaded_state = int(stateFile.readline())
            print("Relay - Loading state from path: {}".format(self.persist_path))
            self.set_state(loaded_state)
        except OSError:
            print("Relay - No persisted state exists yet at path: {}".format(self.persist_path))
            self.relay_off()

    def save_state_to_file(self) -> None:
        with open(self.persist_path, "w+") as state:
            state.write(str(self.state))

