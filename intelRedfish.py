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

    def getAllMetrics(self) -> dict:

        # get all metrics defined for node
        power_cons_dict = {'NodeTotalPower': self.getPowerCons()}

        result = {}
        result = Redfish.mergeDicts(result, self.getSystemMetrics())
        result = Redfish.mergeDicts(result, self.getThermalDict())
        result = Redfish.mergeDicts(result, power_cons_dict)
        return result

    def getPowerCons(self) -> int:

        # intel-specific PSU power read-out

        url = Redfish.mergeUrlElements([self._getChassisURL(self.SYSTEM_I),self.VENDOR_POWER_SUFFIX])
        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)
        power_cons = int(r.json()['PowerControl'][0]['PowerConsumedWatts'])

        return power_cons

    def resetBMC(self):

        # Intel specific BMC reset action
        # - /redfish/v1/Managers/BMC/Actions/Manager.Reset

        API_ENDPOINT = "Actions/Manager.Reset"

        url = Redfish.mergeUrlElements([self._getManagerURL(self.SYSTEM_I), API_ENDPOINT])
        json={"ResetType": "ForceRestart"}
        r = requests.post(url,auth=self.auth_tuple, verify=self.verifySSL, json=json)

    def powerAction(self,action:str):

        # Intel specific chassis power action
        # - /redfish/v1/Systems/{systemID}/Actions/ComputerSystem.Reset

        POWER_ACTIONS = [ "PushPowerButton", "On", "GracefulShutdown", "ForceRestmergeUrlElementseOn", "ForceOff" ]
        API_ENDPOINT = "Actions/ComputerSystem.Reset"

        if action not in POWER_ACTIONS:
            NotImplementedError(f"Action {action} not defined. Only [{','.join(POWER_ACTIONS)}] allowed.")

        url = Redfish.mergeUrlElements([self._getSystemURL(self.SYSTEM_I), API_ENDPOINT ])
        json={"ResetType": action }
        r = requests.post(url,auth=self.auth_tuple, verify=self.verifySSL, json=json)

    def getSystemMetrics(self) -> int:

        # intel-specific metrics
        # - /redfish/v1/Systems/{systemID}/Metrics

        url = Redfish.mergeUrlElements([self._getSystemURL(self.SYSTEM_I), "Metrics"])
        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)

        result = {}
        fields = ["ProcessorPowerWatt", "MemoryPowerWatt", "ProcessorBandwidthPercent", "MemoryBandwidthPercent","IOBandwidthGBps" ]

        for field in fields:
            value = r.json()[field]

            try:
                value_float = float(value)
            except ValueError:
                value_float = None
            if value_float:
                result[field] = value_float

        return(result)
    
    #NOTES:
    # * /redfish/v1/Managers/BMC/VirtualMedia/WebISO/Actions/VirtualMedia.InsertMedia - BROKEN in intel implementation of RedFIsh
    # * /redfish/v1/Managers/BMC/VirtualMedia/WebISO/Actions/VirtualMedia.EjectMedia - BROKEN in intel implementation of RedFIsh




