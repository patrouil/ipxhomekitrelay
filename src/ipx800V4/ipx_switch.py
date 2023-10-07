import pyhap.const

from ipx800V4.ipx_common_onoff   import  IPXCommonOnOff

"""
    relay config settings are
    
        all mandatory IPXAdapter parameters.
        "on" the IPX Command to switch the relay ON i.e. SetR01
        "off" the IPX Command to switch the relay off i.e. ClearR01
"""

class IPXSwitch(IPXCommonOnOff):
    serviceName = "Switch"
    category = pyhap.const.CATEGORY_SWITCH

    def __init__(self, device: dict, driver):
        super().__init__(device, driver, IPXSwitch.serviceName)

#end class