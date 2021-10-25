import requests, json

machine_address = "http://3R-UNIT-01:8000"
url = 'http://3R-UNIT-01:8000/machine/axis_positions'
myobj = {'somekey': 'somevalue'}

x = requests.get(machine_address+"/machine/axis_positions", data = myobj)
positions = json.loads(x.content.decode())
print(f'X position is {positions["x"]}, Z position is {positions["z"]}')

x=requests.post(machine_address+"/machine/gripper", data=data)
data={"gripper_state":"open"}