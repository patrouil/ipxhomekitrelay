import json
import logging

"""
configuration file grammar is 
{
    "homekit" : {
        "pincode" : "XXX-XX-XXX" optionnal
        "bridge_name" : "a name" 
        
    },
    "ipx800" : {
        "host" : "ip or hostname",
        "port" : "portnumber" optionnal
        "apikey" : "XXXXXXXX"
        "interval" : refresh inteerval in ms default 250
    },
    "devices" : [
        {
            "name" : "XXXXX",
            "service" : "nnnnnn",
            "key" : "an IPX get response json variable - R0",
            "room" : "room name", optionnal
            "logging" : "info", "error", "debug" optionnal default "info"
            # device specific commands
            "on" : "SetR=01",
            "off" : "ClearR=01",
        },
    
    ]
}
Available services are : 
    Switch : commands on off
    Lightbubl : commands on off

    TemperatureSensor
    LightSensor
"""


class Configuration:

    def __init__(self, filename='config/config.json'):
        self.config = None
        self.logger = logging.getLogger(__name__)

        with open(filename, "r") as file:
            self.config = json.load(file)
        self.logger.debug("config is  %s", self.config)
        self.check_validity()

    # end constructor

    @property
    def get_homekit(self) -> dict:
        return self.config.get('homekit')

    # end

    @property
    def get_ipx800(self) -> dict:
        return self.config.get("ipx800")

    # end

    @property
    def get_devices(self) -> []:
        return self.config.get("devices")

    # end

    def check_validity(self) -> None:
        c = self.config.get('homekit')
        assert (c.get('bridge_name') is not None)
        # check for mandatory items
        for d in self.config.get('devices'):
            assert (d.get('key') is not None)
            assert (d.get('name') is not None)
            assert (d.get('service') is not None)

    # end
# end class
