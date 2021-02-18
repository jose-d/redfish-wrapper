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

    def getPowerCons(self):

        # supermicro-specific power supply consumption read-out

        system_i = 0

        url = self._getChassisURL(system_i) + self.VENDOR_POWER_SUFFIX

        totalPower = 0

        r = requests.get(url, auth=(
            self.ipmi_user, self.ipmi_pass), verify=self.verifySSL)
        for psu in r.json()['PowerSupplies']:
            totalPower = totalPower + int(psu['LastPowerOutputWatts'])

        return totalPower