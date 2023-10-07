import string
import logging

import pyhap.const
from pyhap.accessory import Accessory
from pyhap.characteristic import Characteristic, HAP_FORMAT_DEFAULTS, PROP_FORMAT

from ipx800V4.ipx_listener import IPXListener

"""
Apple documentation reference

https://developer.apple.com/documentation/homekit

https://developer.apple.com/documentation/homekit/hmcharacteristic/characteristic_types

"""


class IPXAdapter(Accessory, IPXListener):
    category = pyhap.const.CATEGORY_OTHER
    serviceName = None

    logLevelBinding = {
        "info": logging.INFO,
        "error": logging.ERROR,
        "debug": logging.DEBUG,
        "warning": logging.WARNING
    }

    def __init__(self, device, driver):
        assert (device.get('name') is not None)
        assert (device.get('key') is not None)
        super().__init__(driver=driver, display_name=device.get('name'))
        self.initialize()
        self.deviceConfig = device

        self.set_info_service(manufacturer='GCE Electronics', model='IPX800V4')
        self.logger = logging.getLogger(self.display_name)

        l = device.get('logging')
        if l is not None:  # otherwise use global setting
            lvl = IPXAdapter.logLevelBinding.get(l)
            if lvl is not None: self.logger.setLevel(lvl)
        # end if
        self.device_value_pair[self.key] = None
        self.key_characteristics = None  # used

    # end

    @property
    def name(self) -> string:
        return self.deviceConfig.get('name')

    @property
    def deviceService(self) -> string:
        return self.deviceConfig.get('service')

    @property
    def key(self) -> string:
        return self.deviceConfig.get('key')

    @property
    def ipx_value(self) -> string:
        return self.device_value_pair[self.key]

    # override
    def available(self) - > bool:
        return self.ipxStatus

    def default_value(self, car: Characteristic, otherwise: object = None) -> object:
        return HAP_FORMAT_DEFAULTS.get(car.properties.get(PROP_FORMAT, otherwise))

    def get_value_from_ipx(self, car: Characteristic):
        self.logger.debug("get_value_from_ipx: value is %s", car)
        try:
            v = None
            v = self.ipx_value
            return car.to_valid_value(v)
        except Exception as err:
            self.logger.warning("get_value_from_ipx: %s is not a valid value - providing default", v)
            return self.default_value(car)
        # end try

    # end get

    def valueChangedListener(self, device_code: str, new_val: str, old_val: str) -> None:
        self.logger.debug("valueChangedListener: new value for % s : %s -> %s", device_code, old_val, new_val)
        self.device_value_pair[device_code] = new_val
        if device_code == self.key:
            self.key_characteristics.set_value(self.key_characteristics.to_valid_value(new_val))
    # end
# end class
