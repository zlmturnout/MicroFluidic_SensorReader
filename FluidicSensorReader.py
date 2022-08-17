import sys,time
from ctypes import *
from Elveflow64 import *
from array import array

"""
python wrapper for acquiring sensor data 
from Elveflow MicroFluidic Sensor Reader Digital(MSRD)

two types of sensor supported:

1. Flow sensor ->data: uL/min 
2. Pressure sensor ->data: mbar

"""

class ElveflowMSRD(object):
	"""Elveflow MicroFluidic Sensor Reader Digital(MSRD)
	provide A connected instrument name and initialize before further usage
	Args:
		object (_type_): _description_
		name: connected instrument name 
	"""
	def __init__(self,name=None):
		super(ElveflowMSRD, self).__init__()
		self.SensorReaderName = name.encode('ascii')
		self.Instr_ID=c_int32()

	
	def init_SensorReader(self,channel_4list:list,custom_Voltage_2ch:list=[0,0]):
		"""Initialize the Elveflow sensor reader
			
		Args:
			channel_4list: 4 list of sensor types connected to sensor reader i.e.[0,5,10,0]
			custom_Voltage_2ch: Custom Voltage for ch12 and ch34, range 5-25V, default=[0,0]
		Returns:
			tuple: error,Instr_ID
		"""
		error=M_S_R_D_Initialization(self.SensorReaderName,*channel_4list,*custom_Voltage_2ch,byref(self.Instr_ID))
		# error=0 if initialization succeeded,else return error,Instr_ID=-1
		return error, self.Instr_ID.value

	def add_sensor(self,channel:int,sensor_type:int,digital_analog:int,digit_calib:int,digit_resolution:int):
		"""add sensor which is connected to one channel

		Args:
			channel (int): channel to connect to
			sensor_type (int): 
			digital_analog (int): digital=1 analog=0
			digit_calib (int): for Flow sensor, H2O_calibration=0,IPA_calibration=1
			digit_resolution (int): 16 bits resolution=7
		Returns:
			error(int): error code
		"""
		error=M_S_R_D_Add_Sens(self.Instr_ID,channel,sensor_type,digital_analog,digit_calib,digit_resolution)
		return error

	def read_SensorData(self,channel:int):
		"""Read sensor data from one channel

		Args:
			channel (int): channel to connect to
		Returns:
			tuple (int,double): error,data
		"""
		sensor_data=c_double()
		sensor_channel=c_int32(channel)
		error=M_S_R_D_Get_Sens_Data(self.Instr_ID,sensor_channel,byref(sensor_data))
		return error,sensor_data.value
	
	def set_filter(self,channel:int,status:int=0):
		""" set filter on one channel

		Args:
			channel (int): channel number
			status (int):  1 is on , 0 is off
		Returns:
			tuple (int,int): error,status
		"""
		error=M_S_R_D_Set_Filt(self.Instr_ID,channel,status)
		return error,status

	def start_remote_Measureloop(self):
		""" 
		start remote measurement loop which automatically reads all 
		sensor data. No direct call to this MSRD can be made until 
		stop remote measurement loop is called. use get_remote_data
		to acquire the sensor data.

		"""
		error=M_S_R_D_Start_Remote_Measurement(self.Instr_ID)
		return error
	
	def stop_remote__Measureloop(self):
		"""stop_remote__Measureloop
		"""
		error=M_S_R_D_Stop_Remote_Measurement(self.Instr_ID)
		return error
	
	def get_remote_data(self,channel:int):
		"""
		get_remote_data from one channel

		Args:
			channel (int): _description_
		Returns:
			tuple(int,double): error,data
	
		"""
		sensor_data=c_double()
		sensor_channel=c_int32(channel)
		error=M_S_R_D_Get_Remote_Data(self.Instr_ID,sensor_channel,byref(sensor_data))
		return error,sensor_data.value

	def close_SensorReader(self):
		"""close the sensor reader
		Close communication with MSRD
		"""
		error=M_S_R_D_Destructor(self.Instr_ID.value)
		return error

if __name__ == "__main__":
	# bulid MSRD instance name="SensorReader", instrument name from NI MAX(NI USB-8451 "SensorReader")
	SensorReader=ElveflowMSRD(name='SensorReader')
	# initialize the sensor reader
	error_init,ID=SensorReader.init_SensorReader(channel_4list=[0,5,10,0]) # flow senser in ch2,Presurre sensor in ch3
	print('Sensor reader initialized with error: %d\nSensorReader ID: %d' %(error_init,ID))
	# add the two sensor:flow senser in ch2, Presurre sensor in ch3
	error_Flow=SensorReader.add_sensor(channel=2,sensor_type=5,digital_analog=1,digit_calib=0,digit_resolution=7)
	print(f'add flow sensor with error: {error_Flow}')
	error_Press=SensorReader.add_sensor(channel=3,sensor_type=10,digital_analog=0,digit_calib=0,digit_resolution=7)
	print(f'add pressure sensor with error: {error_Press}')
	# Method-1:read the sensor data by call the sensor
	# time.sleep(0.5)
	# error_FlowR,flow_data=SensorReader.read_SensorData(channel=2)
	# print(f'read flow sensor with error: {error_Flow}, data={flow_data}')
	# time.sleep(0.5)
	# error_PressR,press_data=SensorReader.read_SensorData(channel=3)
	# print(f'read pressure sensor with error:{error_PressR}, data={press_data}')
	# Method-2: read the sensor data by remote measurement loop
	time.sleep(0.5)
	error_remote=SensorReader.start_remote_Measureloop()
	time.sleep(0.5)
	error_FlowR,flow_data=SensorReader.get_remote_data(channel=2)
	print(f'read flow sensor with error: {error_FlowR}, data={flow_data}')
	time.sleep(0.5)
	error_PressR,Press_data=SensorReader.get_remote_data(channel=3)
	print(f'read pressure sensor with error:{error_PressR}, data={Press_data}')
	# stop remote measurement loop
	SensorReader.stop_remote__Measureloop()
	# close the sensor reader
	SensorReader.close_SensorReader()