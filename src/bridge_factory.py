import logging

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver

from configuration import Configuration
from device_factory import DeviceFactory


class BridgeFactory:
    """
    devices_definition is the device section of the config file
    devices : [ { dev 1}, {dev 2}, ....]
    """

    def __init__(self, config: Configuration):
        self._config = config
        self._accessories = []
        self.logger = logging.getLogger(__name__)

    # end

    def _get_bridge(self, driver) -> Bridge:
        bridge = Bridge(driver,
                        display_name=self._config.get_homekit.get('bridge_name'))

        for dev_definition in self._config.get_devices:
            acc_instance = DeviceFactory.bind(driver, dev_definition)
            if (acc_instance is not None):
                self._accessories.append(acc_instance)
                self.logger.info("_get_bridge:loading type %s as %s", dev_definition.get('service'),
                                 dev_definition.get('name'))
                bridge.add_accessory(acc_instance)
            else:
                self.logger.error("_get_bridge:no definition for type %s as %s", dev_definition.get('service'),
                                 dev_definition.get('name'))
            # end if
        # end for
        return bridge

    def create_driver(self) -> (AccessoryDriver, []):

        driver = AccessoryDriver(port=self._config.get_homekit.get('port'),
                                 persist_file='config/busy_home.state',
                                 pincode=self._config.get_homekit.get('pincode').encode())

        d = self._get_bridge(driver)
        driver.add_accessory(accessory=d)
        return driver, self._accessories
    #
#
