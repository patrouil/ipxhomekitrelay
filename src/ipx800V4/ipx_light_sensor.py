
import pyhap.const

from ipx800V4.ipx_common_sensor import IPXCommonSensor


class IPXLightSensor(IPXCommonSensor):

    category = pyhap.const.CATEGORY_SENSOR
    serviceName = 'LightSensor'

    def __init__(self, device: dict, driver ):
        super().__init__(device, driver, IPXLightSensor.serviceName, 'CurrentAmbientLightLevel')

