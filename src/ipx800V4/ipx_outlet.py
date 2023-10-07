import pyhap.const

from ipx800V4.ipx_common_onoff import  IPXCommonOnOff

"""
        all mandatory IPXAdapter parameters.
        "on" the IPX Command to switch the outlet ON i.e. SetR01
        "off" the IPX Command to switch the outlet off i.e. ClearR01

"""
class IPXOutlet(IPXCommonOnOff):

    category = pyhap.const.CATEGORY_OUTLET
    serviceName = 'Outlet'

    def __init__(self, device: dict, driver ):
        super().__init__(device, driver,  IPXOutlet.serviceName)

#end class