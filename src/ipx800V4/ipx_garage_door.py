import pyhap.const
from pyhap.accessory import Accessory

from ipx800V4.ipx_adapter import IPXAdapter

"""
    "RequiredCharacteristics": [
         "CurrentDoorState", 
             "Closed": 1,
             "Closing": 3,
             "Open": 0,
             "Opening": 2,
             "Stopped": 4
      }
         "TargetDoorState",
                "Closed": 1,
                "Open": 0
         "ObstructionDetected"
           "Format": "bool",
      ],
      
      attribs
      key : current state : 0 close  / 1 open
      open : open command
      close : close command
      obstruction : obstruction detection
      """


class IPXGarageDoorOpener(IPXAdapter):
    category = pyhap.const.CATEGORY_GARAGE_DOOR_OPENER
    serviceName = "GarageDoorOpener"

    CLOSED_STATE = 1
    CLOSING_STATE = 3
    OPEN_STATE = 0
    OPENING_STATE = 2
    STOPPED_STATE = 4

    def __init__(self, device: dict, driver, ):
        super().__init__(device, driver)
        service = self.add_preload_service(IPXGarageDoorOpener.serviceName)
        self.key_characteristics = service.configure_char('CurrentDoorState')

        self.target_pos = service.configure_char(
            'TargetDoorState', setter_callback=self.set_position)

        self.obstruction_key = self.deviceConfig.get("obstruction", None)
        if self.obstruction_key is not None:
            self.device_value_pair[self.obstruction_key] = None
            self.obstruction_char = service.configure_char('ObstructionDetected')
        self._state = IPXGarageDoorOpener.OPEN_STATE
        self._obstruction = False
        return
    # end


    def _device_value_to_state(self, val: str) -> int:
        self._state = IPXGarageDoorOpener.CLOSED_STATE \
            if val else IPXGarageDoorOpener.OPEN_STATE
        return self._state
    #

    def _target_value_to_state(self, val: bool) -> int:
        self._state = IPXGarageDoorOpener.CLOSING_STATE \
            if val else IPXGarageDoorOpener.OPENING_STATE
        return self._state

    # end

    def _ipx_device_to_obstruction(self, val: str):
        if self.obstruction_key is None:
            return
        self._obstruction = not (val == "1")
        return
    # end

    def set_position(self, value: bool = False) -> None:
        k = "close" if value else "open"
        cmd = self.deviceConfig.get(k)
        self.logger.info("set_position: value is: %s and cmd is %s", value, cmd)
        if cmd is not None:
            self.action_command_callback(cmd)
            self._target_value_to_state(value)
            # state is Opening of Closing based on received command
            self.key_characteristics.set_value(self._state)
        # end if
        return
    # end def

    def get_position(self) -> int:
        self.logger.debug("get_position: state %d", self._state)
        return self._state

    # end

    @Accessory.run_at_interval(5)
    async def run(self):
        v = self.ipx_value
        if ( self._state  == IPXGarageDoorOpener.CLOSING_STATE
                or self._state  == IPXGarageDoorOpener.OPENING_STATE ) :
            self.valueChangedListener(self.key, v, v)
        return

    # override
    def valueChangedListener(self, device_code: str, new_val: str, old_val: str) -> None:
        self.logger.debug("valueChangedListener: new value for % s : %s -> %s ", device_code, old_val, new_val)
        self.device_value_pair[device_code] = new_val
        if (device_code == self.key):
            self._device_value_to_state(new_val)
            self.key_characteristics.set_value(
                self._state)  # key characteristice handler by parent class let check obstrucation
        obstruction_key = self.deviceConfig.get("obstruction", None)
        if (device_code == obstruction_key):
            # @TODO : convert and store in _obstruction
            self.obstruction_char.set_value(self._obstruction)
        self.logger.debug("valueChangedListener: publish state %d : value %d", self._state, new_val)

        return
    # end
# end class
