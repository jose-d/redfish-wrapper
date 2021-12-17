from abc import abstractmethod, ABCMeta
import re
import urllib3
import urllib.parse
import requests
import logging
from functools import reduce
import typing

class Redfish(metaclass=ABCMeta):
   
    TYPE = "REDFISH"
    SYSTEM_PREFIX = '/redfish/v1/Systems'
    CHASSIS_PREFIX = '/redfish/v1/Chassis'
    MANAGER_PREFIX = '/redfish/v1/Managers'

    T_list_str = typing.List[str]

    def __init__(self, ipmi_host:str, ipmi_user:str, ipmi_pass:str, verifySSL:str, name:str):

        logging.basicConfig(level=logging.WARNING)

        self.ipmi_ip = ipmi_host
        self.ipmi_user = ipmi_user
        self.ipmi_pass = ipmi_pass
        self.auth_tuple = (self.ipmi_user, self.ipmi_pass)
        self.verifySSL = verifySSL
        self.name = name

        self._buildBaseUrl(ipmi_host)

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

    def _getSystemURL(self, i:int) -> str:

        return Redfish.mergeUrlElements([self.url_base, self.SYSTEM_PREFIX, self.systems[i]])


    def _getChassisURL(self, i:int) -> str:

        return Redfish.mergeUrlElements([self.url_base, self.CHASSIS_PREFIX, self.chassis[self.systems[i]]])


    def _getManagerURL(self, i:int) -> str:

        return Redfish.mergeUrlElements([self.url_base, self.MANAGER_PREFIX, self.managers[self.systems[i]]])


    @staticmethod
    def _prependHttpWhenMissing(url:str) -> str:

        if not re.match('(?:http|https)://', url):
            return f'http://{url}'
        return url

    @staticmethod
    def mergeDicts(dict1:dict, dict2:dict) -> dict:
        """ merge dicts
        ref: https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python-taking-union-o
        """

        mergedDict = {**dict1, **dict2}
        return mergedDict

    def _buildBaseUrl(self, ipmi_host:str) -> str:

        self.url_base = Redfish._prependHttpWhenMissing(ipmi_host)

    def _parseSystems(self) -> dict:
        return self.__getMembers(self.SYSTEM_PREFIX)

    @staticmethod
    def __getLastElementFromUrl(url:str) -> str:
        """ something/else/element -> returns "element" """
        return url.rsplit('/', 1)[-1]

    @staticmethod
    def __appendTrailingSlashIfMissing(url:str) -> str:
        return str(url) + '/' if not url.endswith('/') else url

    @staticmethod
    def mergeUrlElements(urls:T_list_str) -> str:
        """ from [ 'https://foo.bar','bre','keke' ] makes "https://foo.bar/bre/keke" """

        for url in urls:
            url_index = urls.index(url)
            urls[url_index] = Redfish.__appendTrailingSlashIfMissing(url)

        return reduce(urllib.parse.urljoin, urls)

    def __getSystemJSONs(self) -> dict:

        systemJSONs = []

        for system in self.systems:
            url = Redfish.mergeUrlElements([self.url_base, self.SYSTEM_PREFIX, system])
            r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)
            systemJSONs.append(r.json())

        return systemJSONs


    def _parseChassis(self) -> dict:

        chassis_dict = {}

        for system,systemJSON in zip(self.systems,self.systemsJSON):
            chassis_dict[system] = str(Redfish.__getLastElementFromUrl(systemJSON['Links']['Chassis'][0]['@odata.id']))

        return chassis_dict

    def _parseManagers(self) -> dict:

        managers_dict = {}

        for system,systemJSON in zip(self.systems,self.systemsJSON):
            managers_dict[system] = str(Redfish.__getLastElementFromUrl(systemJSON['Links']['ManagedBy'][0]['@odata.id']))

        return managers_dict

    def __getMembers(self, url) -> T_list_str:

        url = Redfish.mergeUrlElements([self.url_base,url])
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

    def getPowerState(self) -> str:

        system_i = 0
        url = self._getSystemURL(system_i)
        r = requests.get(url, auth=self.auth_tuple, verify=self.verifySSL)

        return r.json()['PowerState']

    def getThermalDict(self) -> dict:

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
