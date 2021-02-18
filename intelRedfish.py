import re
import urllib3
import urllib.parse
import requests
import sys
from redfishwrapper.redfish import Redfish


class IntelRedfish(Redfish):

    # vendor-specific API endpoints:
    VENDOR_THERMAL_SUFFIX = 'Baseboard/Thermal'
    VENDOR_POWER_SUFFIX = 'Baseboard/Power'
    SYSTEM_I = 0
    POWER_ACTIONS = [ "PushPowerButton", "On", "GracefulShutdown", "ForceRestart", "Nmi", "ForceOn", "ForceOff" ]

    def getPowerCons(self):

        # intel-specific PSU power read-out

        url = self._getChassisURL(self.SYSTEM_I) + self.VENDOR_POWER_SUFFIX
        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)
        power_cons = int(r.json()['PowerControl'][0]['PowerConsumedWatts'])

        return power_cons

    def resetBMC(self):

        # Intel specific BMC reset action
        # - /redfish/v1/Managers/BMC/Actions/Manager.Reset

        url = self._getManagerURL(self.SYSTEM_I) + "Actions/Manager.Reset"
        json={"ResetType": "ForceRestart"}
        r = requests.post(url,auth=self.auth_tuple, verify=self.verifySSL, json=json)

    def powerAction(self,action):

        # Intel specific chassis power action
        # - /redfish/v1/Systems/{systemID}/Actions/ComputerSystem.Reset

        if action not in self.POWER_ACTIONS:
            raise NotImplementedError(f"Action {action} not defined. Only [{','.join(self.POWER_ACTIONS)}] allowed.")

        url = self._getSystemURL(self.SYSTEM_I) + "Actions/ComputerSystem.Reset"
        json={"ResetType": action }
        r = requests.post(url,auth=self.auth_tuple, verify=self.verifySSL, json=json)


    # nope: this is broken:
    #def inject media: /redfish/v1/Managers/BMC/VirtualMedia/WebISO/Actions/VirtualMedia.InsertMedia
    #def eject media:  /redfish/v1/Managers/BMC/VirtualMedia/WebISO/Actions/VirtualMedia.EjectMedia

    #def getall metrics: get everythign (to be pushed into influx or so..)

   #def advanced metrics:
        # intel specific metrics:
        #https://XXXX/redfish/v1/Systems/ASDASDASDASDASDASD/Metrics:
   #         # {
   #     "@odata.context": "/redfish/v1/$metadata#ComputerSystemMetrics.ComputerSystemMetrics",
   #     "@odata.id": "/redfish/v1/Systems/BQF974900048/Metrics",
   #     "@odata.type": "#ComputerSystemMetrics.v1_0_0.ComputerSystemMetrics",
   #     "Name": "Computer System Metrics",
   #     "Id": "1",
   #     "Health": [
   #         "OK"
   #     ],
   #     "ProcessorPowerWatt": 232.9150390625,
   #     "MemoryPowerWatt": 71.517333984375,
   #     "ProcessorBandwidthPercent": 76,
   #     "MemoryBandwidthPercent": 97,
   #     "IOBandwidthGBps": 2,
   #     "MemoryThrottledCyclesPercent": null,
   # "@odata.etag": "c5695287eb4a58234dcbbc1e67c48442"



