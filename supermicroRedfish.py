import re
import urllib3
import urllib.parse
import requests
import sys
from redfishwrapper.redfish import Redfish

class SupermicroRedfish(Redfish):

    VENDOR_POWER_PREFIX = '/redfish/v1/Chassis/1/Power'

    def getPowerCons(self):
        totalPower = 0
        url = urllib.parse.urljoin(self.url_base, self.VENDOR_POWER_PREFIX)
        r = requests.get(url, auth=(self.ipmi_user, self.ipmi_pass), verify=self.verifySSL)
        for psu in r.json()['PowerSupplies']:
            totalPower = totalPower + int(psu['LastPowerOutputWatts'])

        return totalPower

