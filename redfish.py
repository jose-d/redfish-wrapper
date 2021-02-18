from abc import abstractmethod, ABCMeta
import re
import urllib3
import urllib.parse
import requests
import logging
from functools import reduce


class Redfish(metaclass=ABCMeta):

    TYPE = "REDFISH"
    SYSTEM_PREFIX = '/redfish/v1/Systems'
    CHASSIS_PREFIX = '/redfish/v1/Chassis'
    MANAGER_PREFIX = '/redfish/v1/Managers'

    def __init__(self, ipmi_ip, ipmi_user, ipmi_pass, verifySSL):

        logging.basicConfig(level=logging.INFO)

        self.ipmi_ip = ipmi_ip
        self.ipmi_user = ipmi_user
        self.ipmi_pass = ipmi_pass
        self.auth_tuple = (self.ipmi_user, self.ipmi_pass)
        self.verifySSL = verifySSL

        self._buildBaseUrl(ipmi_ip)

        if not verifySSL:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.systems = self._parseSystems()  # get systems managed by this redfish device:
        self.systemsJSON = self.__getSystemJSONs()  # save the jsons to have them cached for later:

        self.chassis = self._parseChassis()  # get first chassis for each system.
        self.managers = self._parseManagers()   # get first manager for each system.

        # debug only:
        for system in self.systems:
            logging.info(
                f"system: {system} is in chassis {self.chassis[system]}")

        logging.info(f"_getSystemURL(0): {self._getSystemURL(0)}")
        logging.info(f"_getChassisURL(0): {self._getChassisURL(0)}")
        logging.info(f"_getManagerURL(0): {self._getManagerURL(0)}")

    def _getSystemURL(self, i):

        return Redfish.__mergeUrlElements([self.url_base, self.SYSTEM_PREFIX, self.systems[i]])


    def _getChassisURL(self, i):

        return Redfish.__mergeUrlElements([self.url_base, self.CHASSIS_PREFIX, self.chassis[self.systems[i]]])


    def _getManagerURL(self, i):

        return Redfish.__mergeUrlElements([self.url_base, self.MANAGER_PREFIX, self.managers[self.systems[i]]])


    @staticmethod
    def _prependHttpWhenMissing(url):

        if not re.match('(?:http|https)://', url):
            return f'http://{url}'
        return url

    def _buildBaseUrl(self, ipmi_ip):

        self.url_base = Redfish._prependHttpWhenMissing(ipmi_ip)

    def _parseSystems(self):
        return self.__getMembers(self.SYSTEM_PREFIX)

    @staticmethod
    def __getLastElementFromUrl(url):
        """ something/else/element -> returns "element" """
        return url.rsplit('/', 1)[-1]

    @staticmethod
    def __appendTrailingSlashIfMissing(url):
        return str(url) + '/' if not url.endswith('/') else url

    @staticmethod
    def __mergeUrlElements(urls):
        """ from [ 'https://foo.bar','bre','keke' ] makes "https://foo.bar/bre/keke" """

        for url in urls:
            url_index = urls.index(url)
            urls[url_index] = Redfish.__appendTrailingSlashIfMissing(url)

        return reduce(urllib.parse.urljoin, urls)

    def __getSystemJSONs(self):

        systemJSONs = []

        for system in self.systems:
            url = Redfish.__mergeUrlElements([self.url_base, self.SYSTEM_PREFIX, system])
            r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)
            systemJSONs.append(r.json())

        return systemJSONs


    def _parseChassis(self):

        chassis_dict = {}

        for system,systemJSON in zip(self.systems,self.systemsJSON):
            chassis_dict[system] = str(Redfish.__getLastElementFromUrl(systemJSON['Links']['Chassis'][0]['@odata.id']))

        return chassis_dict

    def _parseManagers(self):

        managers_dict = {}

        for system,systemJSON in zip(self.systems,self.systemsJSON):
            #print(systemJSON['Links']['ManagedBy'][0]['@odata.id'])
            managers_dict[system] = str(Redfish.__getLastElementFromUrl(systemJSON['Links']['ManagedBy'][0]['@odata.id']))

        return managers_dict

    def __getMembers(self, url):

        url = Redfish.__mergeUrlElements([self.url_base,url])
        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)
        members = r.json()['Members']
        result_list = []

        for item in members:
            result_list.append(
                Redfish.__getLastElementFromUrl(item['@odata.id']))

        return result_list

    # abstract methods:

    @abstractmethod
    def getPowerCons(self):
        """ vendor-specific, to be implemented in child class """
        return NotImplemented

    # methods working across vendors

    def getPowerState(self):

        system_i = 0
        url = self._getSystemURL(system_i)
        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)

        return r.json()['PowerState']

    def getThermalDict(self):

        system_i = 0

        url = self._getChassisURL(system_i) + self.VENDOR_THERMAL_SUFFIX
        thermal_dict = {}

        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)
        temperatures = r.json()['Temperatures']
        for item in temperatures:
            name = item['Name']
            value = item['ReadingCelsius']
            thermal_dict[name] = value

        return(thermal_dict)
