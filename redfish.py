import re
import urllib3



class Redfish:

    TYPE="REDFISH"

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
