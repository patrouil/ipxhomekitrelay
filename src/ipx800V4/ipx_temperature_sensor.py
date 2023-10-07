
import pyhap.const

from ipx800V4.ipx_common_sensor import IPXCommonSensor


class IPXTemperatureSensor(IPXCommonSensor):

    category = pyhap.const.CATEGORY_SENSOR
    serviceName = 'TemperatureSensor'

    def __init__(self, device: dict, driver, ):
        super().__init__(device, driver, IPXTemperatureSensor.serviceName, 'CurrentTemperature')
