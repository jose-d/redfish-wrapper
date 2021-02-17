import re
import urllib3
import urllib.parse
import requests
import sys


class IntelRedfish:

    TYPE="REDFISH"
    VENDOR_THERMAL_PREFIX = '/redfish/v1/Chassis/RackMount/Baseboard/Thermal'
    VENDOR_POWER_PREFIX = '/redfish/v1/Chassis/RackMount/Baseboard/Power'

    def __init__(self, ipmi_ip, ipmi_user, ipmi_pass, verifySSL):

        self.ipmi_ip = ipmi_ip
        self.ipmi_user = ipmi_user
        self.ipmi_pass = ipmi_pass
        self.verifySSL = verifySSL

        self._buildBaseUrl(ipmi_ip)

        if not verifySSL:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _prependHttpWhenMissing(self, url):
        if not re.match('(?:http|https)://', url):
            return f'http://{url}'
        return url
    
    def _buildBaseUrl(self,ipmi_ip):
        self.url_base = self._prependHttpWhenMissing(ipmi_ip)

    def getPowerCons(self):

        url = urllib.parse.urljoin(self.url_base, self.VENDOR_POWER_PREFIX)
        
        r = requests.get(url, auth=(self.ipmi_user, self.ipmi_pass), verify=self.verifySSL)
        power_cons = int(r.json()['PowerControl'][0]['PowerConsumedWatts'])

        return power_cons

