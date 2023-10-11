import pyhap.const
from pyhap.accessory import Accessory

from ipx800V4.ipx_adapter import IPXAdapter

"""
    window shutter config settings are
    
        all mandatory IPXAdapter parameters.
        change change shutter leveL;
"""


class IPXWindowCovering(IPXAdapter):
    category = pyhap.const.CATEGORY_WINDOW_COVERING
    serviceName = "WindowCovering"

    POS_STATE_closing = 0
    POS_STATE_Opening = 1
    POS_STATE_Stopped = 2

    def __init__(self, device: dict, driver, ) -> None:
        super().__init__(device, driver)
        service = self.add_preload_service(IPXWindowCovering.serviceName)

        self.key_characteristics = service.configure_char(
            'CurrentPosition')

        self.target_poss = service.configure_char(
            'TargetPosition', setter_callback=self.set_position)

        self.pos_state = service.configure_char(
            'PositionState', getter_callback=self.get_state)

        self._lastLevel = None  # for IPX zero mean open
        self._curr_state = IPXWindowCovering.POS_STATE_Stopped
        return

    # end

    def _to_ipx_range(self, val: int) -> int:
        return -val + 100

    # end

    def _to_homekit_range(self, val: int) -> int:
        return -val + 100

    # end

    def set_position(self, value=0) -> None:
        cmd = self.deviceConfig.get('change')
        command = cmd % self._to_ipx_range(value)
        self.logger.info("set_position: value is: %s and cmd is %s", value, command)
        if cmd is not None:
            self.action_command_callback(command)
        return

    # end def

    def _set_state_by_position(self, vr_pos: int) -> None:
        if (self._curr_state is None or self._lastLevel is None or
                vr_pos == 0 or vr_pos == 100):
            self._curr_state = IPXWindowCovering.POS_STATE_Stopped
        elif (vr_pos > self._lastLevel):
            self._curr_state = IPXWindowCovering.POS_STATE_closing
        elif (vr_pos < self._lastLevel):
            self._curr_state = IPXWindowCovering.POS_STATE_Opening
        else:
            self._curr_state = IPXWindowCovering.POS_STATE_Stopped
        self._lastLevel = vr_pos
        return

    # end

    def get_state(self):
        self.logger.debug("get_state: value is %d", self._curr_state)
        return self._curr_state

    # end

    @Accessory.run_at_interval(5)
    async def run(self):
        v = self.ipx_value
        if ( self._curr_state != IPXWindowCovering.POS_STATE_Stopped) :
            self.valueChangedListener(self.key, v, str(self._lastLevel))
        return

    def valueChangedListener(self, device_code: str, new_val: str, old_val: str) -> None:
        self.logger.debug("valueChangedListener: new value for % s : %s -> %s", device_code, old_val, new_val)
        self.device_value_pair[device_code] = new_val
        if device_code == self.key:
            self._set_state_by_position(int(new_val))
            p = self._to_homekit_range(int(new_val))
            self.key_characteristics.set_value(p)  # key characteristice handler by parent class let chel obstrucation
            self.pos_state.set_value(self._curr_state)
            self.logger.debug("valueChangedListener: publish state %s : level %s", self._curr_state, p)
        return
    # end if
    # end
# end class
