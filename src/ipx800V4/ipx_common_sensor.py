import pyhap.const

from ipx800V4.ipx_adapter import IPXAdapter

class IPXCommonSensor(IPXAdapter):

    category = pyhap.const.CATEGORY_SENSOR

    def __init__(self, device: dict, driver: object, serviceName: str, required_char_name: str):
        super().__init__(device, driver)
        service = self.add_preload_service(serviceName)
        self.key_characteristics = service.configure_char(
            required_char_name)
        return
    #end
# end class
