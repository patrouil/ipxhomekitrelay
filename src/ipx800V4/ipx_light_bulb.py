import pyhap.const

from ipx800V4.ipx_common_onoff import  IPXCommonOnOff

class IPXLightbulb(IPXCommonOnOff):

    category = pyhap.const.CATEGORY_LIGHTBULB
    serviceName = 'Lightbulb'

    def __init__(self, device: dict, driver ):
        super().__init__(device, driver, IPXLightbulb.serviceName)
