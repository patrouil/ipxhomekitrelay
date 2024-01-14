"""
   "ContactSensor": {
      "OptionalCharacteristics": [
         "StatusActive",
         "StatusFault",
         "StatusTampered",
         "StatusLowBattery",
         "Name"
      ],
      "RequiredCharacteristics": [
         "ContactSensorState"   0 detected 1 not detected. same as most IPX
      ],
      "UUID": "00000080-0000-1000-8000-0026BB765291"
   },


"""
import pyhap.const

from ipx800V4.ipx_common_sensor import IPXCommonSensor



class IPXOccupancySensor(IPXCommonSensor):
    category = pyhap.const.CATEGORY_SENSOR
    serviceName = 'OccupancySensor'

    def __init__(self, device: dict, driver):
        super().__init__(device, driver, IPXOccupancySensor.serviceName, 'OccupancyDetected')
        return

    def valueChangedListener(self, device_code: str, new_val: str, old_val: str) -> None:
        self.logger.debug("valueChangedListener: contact for % s : %s -> %s", device_code, old_val, new_val)
        self.device_value_pair[device_code] = new_val
        if device_code == self.key:
            k = int(new_val)
            self.key_characteristics.set_value(self.key_characteristics.to_valid_value(k))
        return
# end
