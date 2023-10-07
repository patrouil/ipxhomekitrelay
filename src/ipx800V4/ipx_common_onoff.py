import pyhap.const

from ipx800V4.ipx_adapter import IPXAdapter

"""
    relay config settings are
    
        all mandatory IPXAdapter parameters.
        "on" the IPX Command to switch the relay ON i.e. SetR01
        "off" the IPX Command to switch the relay off i.e. ClearR01
"""


class IPXCommonOnOff(IPXAdapter):
    category = pyhap.const.CATEGORY_OTHER

    def __init__(self, device: dict, driver, serviceName: str):
        super().__init__(device, driver)
        service = self.add_preload_service(serviceName)

        self.key_characteristics = service.configure_char(
            'On', setter_callback=self.set_onoff)
        return

    def set_onoff(self, value=False) -> None:
        k = "on" if value else "off"
        cmd = self.deviceConfig.get(k)
        self.logger.info("set_onoff: value is: %s and cmd is %s", value, cmd)
        try:
            if cmd is not None:
                self.action_command_callback(cmd)
        except Exception as err:
            self.logger.error("set_onoff: setting error %s", err)
        return
        # end

    # end def

    def get_onoff(self):
        self.logger.debug("get_onoff: ")
        try:
            return self.key_characteristics.to_valid_value(self.ipx_value)
        except Exception as err:
            self.logger.warning("get_onoff: no value for %s - providing default", self.key)
            return self.default_value(self.key_characteristics)
        # end try
        return
    # end

# end class
