class IPXListener:
    # no constructor. Unable to use in multiple inheritance
    def initialize(self):
        self.ipxStatus = False
        self.device_value_pair = {}
    #

    async def valueChangedListener(self, device_code: str, new_val: str, old_val: str) -> None:
        pass
    #
    def listenedDevices(self) -> []:
        return list(self.device_value_pair)
    #

    def ipxStatusChangedListener(self, isReady: bool) -> None:
        self.ipxStatus = isReady

    def setCommandCallback(self, func) -> None:
        self.action_command_callback = func
# end class
