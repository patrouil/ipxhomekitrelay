import logging

from ipx800V4.ipx_adapter import IPXAdapter
from ipx800V4.ipx_garage_door import IPXGarageDoorOpener
from ipx800V4.ipx_light_sensor import IPXLightSensor
from ipx800V4.ipx_switch import IPXSwitch
from ipx800V4.ipx_temperature_sensor import IPXTemperatureSensor
from ipx800V4.ipx_light_bulb import IPXLightbulb
from ipx800V4.ipx_window_covering import IPXWindowCovering
from ipx800V4.ipx_outlet import IPXOutlet
from ipx800V4.ipx_contact_sensor import IPXContactSensor
from ipx800V4.ipx_motion_sensor import IPXMotionSensor
from ipx800V4.ipx_occupancy_sensor import IPXOccupancySensor

_device_association = {
    IPXGarageDoorOpener.serviceName: IPXGarageDoorOpener,
    IPXLightbulb.serviceName: IPXLightbulb,
    IPXLightSensor.serviceName: IPXLightSensor,
    IPXSwitch.serviceName: IPXSwitch,
    IPXOutlet.serviceName: IPXOutlet,
    IPXTemperatureSensor.serviceName: IPXTemperatureSensor,
    IPXWindowCovering.serviceName: IPXWindowCovering,
    IPXContactSensor.serviceName : IPXContactSensor,
    IPXMotionSensor.serviceName : IPXMotionSensor,
    IPXOccupancySensor.serviceName : IPXOccupancySensor

}

class DeviceFactory:

    _logger = logging.getLogger(__name__)

    @staticmethod
    def bind(driver, deviceConfig) -> IPXAdapter:
        t = deviceConfig.get("service")
        assert (t is not None)
        d = _device_association.get(t)
        if d is None:
            DeviceFactory._logger.error("device service is invalid: >%s<", t)
            return None
        return d(device=deviceConfig, driver=driver)

# end class
