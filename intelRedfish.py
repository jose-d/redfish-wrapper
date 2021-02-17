import re
import urllib3
import urllib.parse
import requests
import sys
from redfishwrapper.redfish import Redfish


class IntelRedfish(Redfish):

    VENDOR_THERMAL_PREFIX = '/redfish/v1/Chassis/RackMount/Baseboard/Thermal'
    VENDOR_POWER_PREFIX = '/redfish/v1/Chassis/RackMount/Baseboard/Power'

    def getPowerCons(self):

        url = urllib.parse.urljoin(self.url_base, self.VENDOR_POWER_PREFIX)
        
        r = requests.get(url, auth=(self.ipmi_user, self.ipmi_pass), verify=self.verifySSL)
        power_cons = int(r.json()['PowerControl'][0]['PowerConsumedWatts'])

        return power_cons

    def getThermalDict(self):

        url = urllib.parse.urljoin(self.url_base, self.VENDOR_THERMAL_PREFIX)

        thermal_dict = {}

        r = requests.get(url, auth=(self.ipmi_user, self.ipmi_pass), verify=self.verifySSL)
        temperatures = r.json()['Temperatures']
        for item in temperatures:
            name = item['Name']
            value = item['ReadingCelsius']
            thermal_dict[name] = value

        return(thermal_dict)

