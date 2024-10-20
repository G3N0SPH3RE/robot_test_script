import base64, hashlib, yaml, httpx, os, time
from threading import Thread
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, ClassVar, Any

from . import ROOT_PATH, CONFIG_FILE_DIRECTORY


class MiRCommunicationException(Exception):
    pass


class MiROperatingModes(Enum):
    READY = 3
    PAUSE = 4
    EXECUTING = 5
    IDLE = 7


@dataclass
class MiR:
    name: str
    #configuration_file_name: str

    configuration: Dict[str, Any]
    missions: ClassVar[Dict[str, Dict[str, Any]]] = {}  # = field(default_factory=dict)
    registers: ClassVar[Dict[int, float]] = {}  # = field(default_factory=dict)

    operating_mode: ClassVar[int] = -1

    authentication_header: ClassVar[Dict]

    def __post_init__(self):
        # super(MiR, self).__init__()
        # with open(os.path.join(ROOT_PATH, CONFIG_FILE_DIRECTORY, self.configuration_file_name), 'r') as config_file:
        #     self.configuration = yaml.load(config_file, loader=yaml.Loader)

        self.create_authentication_header()
        self.api_url = 'http://' + self.configuration['communication']['ip_address'] + '/' + \
                       self.configuration['communication']['api_path']

        self.get_mission_guids()

    def create_authentication_header(self):
        self.authentication_header = {
            'Authorization': 'Basic ' + base64.b64encode(
                (self.configuration['communication']['username'] + ':').encode() + \
                hashlib.sha256(self.configuration['communication']['password'].encode()).hexdigest().encode()).decode()
        }

    def create_request_url(self, endpoint: str) -> str:
        return '/'.join([self.api_url, endpoint])

    def get_mir_data(self, endpoint: str) -> httpx.Response:
        try:
            return httpx.get(self.create_request_url(endpoint), headers=self.authentication_header, timeout=self.configuration['communication']['timeout_seconds'])
        except httpx.ConnectTimeout:
            print('timed out on GET ' + endpoint)
            return httpx.Response(status_code=404)
        except httpx.ConnectError:
            print('no route to host on GET ' + endpoint)
            return httpx.Response(status_code=404)
        except Exception as e:
            #self.logger.error(f"Robot {self.name} encountered exception on GET {endpoint}: " + e.args[0])
            a=5

    def get_mission_guids(self):
        #mir_missions = httpx.get(self.create_request_url('missions'), headers=self.authentication_header, timeout=self.configuration['communication']['timeout_seconds']).json()
        result = self.get_mir_data('missions')
        if result.is_success:
            for mission in result.json():
                if mission['name'] in self.missions.keys():
                    self.missions[mission['name']] = mission

    def get_plc_registers(self):
        #registers = httpx.get(self.create_request_url('registers'), headers=self.authentication_header).json()
        result = self.get_mir_data('registers')
        if result.is_success:
            for register in result.json():
                self.registers[register['id']] = register['value']

    def get_robot_status(self):
        #result = httpx.get(self.create_request_url('status'), headers=self.authentication_header)
        result = self.get_mir_data('status')
        # self.operating_mode = state['mode_id']
        if result.is_success:
            response_data = result.json()
            #self.operating_mode = MiROperatingModes(response_data['mode_id'])
            print('Robot state name is: ' + response_data['state_text'] + ' and robot state id is: ' + str(
                response_data['state_id']))
        # else:
        #     raise MiRCommunicationException

    def set_robot_operating_mode(self, state: MiROperatingModes) -> bool:
        result = httpx.put(self.create_request_url('status'), data={'mode_id': state.value})
        if result.is_success:
            return True
        return False

    def enqueue_mission(mission_guid: str):
        pass

    def check_robot_in_position(position_guid: str) -> bool:
        pass


class MiRController(Thread):
    def __init__(self, configuration_file_name: str):
        super(MiRController, self).__init__()

        self.robots = {}
        self.initialize_fleet(configuration_file_name)
        #self.mir200 = MiR(configuration_file_name)

    def initialize_fleet(self, configuration_file_name: str):
        with open(os.path.join(ROOT_PATH, CONFIG_FILE_DIRECTORY, configuration_file_name), 'r') as config_file:
            config = yaml.load(config_file, Loader=yaml.Loader)
            for robot_name in config['fleet']['robots_deployed']:
                self.robots[robot_name] = (MiR(name=robot_name, configuration=config[robot_name]))
            #self.configuration = yaml.load(config_file)

    def run(self):
        while True:
            self.robots['mir200_0'].get_robot_status()
            self.robots['mir200_0'].get_plc_registers()
            time.sleep(1)
