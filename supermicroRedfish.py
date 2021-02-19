import re
import urllib3
import urllib.parse
import requests
import sys
from redfishwrapper.redfish import Redfish


class SupermicroRedfish(Redfish):

    # vendor-specific API endpoints:
    VENDOR_THERMAL_SUFFIX = '/Thermal'
    VENDOR_POWER_SUFFIX = '/Power'
    SYSTEM_I = 0

    def getAllMetrics(self) -> dict:

        # get all metrics defined for node
        power_cons_dict = {'NodeTotalPower': self.getPowerCons()}

        result = {}
        result = Redfish.mergeDicts(result, self.getThermalDict())
        result = Redfish.mergeDicts(result, power_cons_dict)

        return result


    def getPowerCons(self) -> int:

        # supermicro-specific power supply consumption read-out

        url = self._getChassisURL(self.SYSTEM_I) + self.VENDOR_POWER_SUFFIX

        totalPower = 0

        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)
        for psu in r.json()['PowerSupplies']:
            totalPower = totalPower + int(psu['LastPowerOutputWatts'])

        return totalPower

    def powerAction(self,action:str): #TODO: Untested!!!

        POWER_ACTIONS = ["On", "ForceOff", "GracefulShutdown", "GracefulRestart", "ForceRestart", "Nmi", "ForceOn" ]
        API_ENDPOINT = "Actions/ComputerSystem.Reset"

        if action not in POWER_ACTIONS:
            raise NotImplementedError(f"Action {action} not defined. Only [{','.join(POWER_ACTIONS)}] allowed.")
        
        url = self._getSystemURL(self.SYSTEM_I) + API_ENDPOINT
        json={"ResetType": action }
        r = requests.post(url,auth=self.auth_tuple, verify=self.verifySSL, json=json)
