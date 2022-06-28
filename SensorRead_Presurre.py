from re import S
import sys,time
from _ast import Load
sys.path.append('DLL64')#add the path of the library here
#sys.path.append('E:/Coding/PythonProjects/MSensorReaderDigital')#add the path of the LoadElveflow.py

from ctypes import *

from array import array

from Elveflow64 import *


#
#Initialization of MSRD ( ! ! ! REMEMBER TO USE .encode('ascii') ! ! ! )
#
Instr_ID=c_int32()
print("Instrument name and sensor types are hardcoded in the Python script")
#see User Guide to determine sensor types and NIMAX software to determine the instrument name (installed with ESI)
error=M_S_R_D_Initialization('SensorReader'.encode('ascii'),0,5,10,0,0,0,byref(Instr_ID)) 
#(CustomSens_Voltage_Ch12 and Ch34 is used for CustomSensors only, voltage is between 5 and 25V)
#all functions will return error code to help you to debug your code, for further information see User Guide
print('error:%d' % error)
print("MSRD ID: %d" % Instr_ID.value)

#add sensor
error=M_S_R_D_Add_Sens(Instr_ID,Channel_1_to_4=3,SensorType=10,DigitalAnalog=0,FSens_Digit_Calib=0,FSens_Digit_Resolution=7) #add digital flow sensor, if not found throw error 8000. remember that channel 1-2 or 3-4 should be of the same kind. sensor type should be the same as in the initialization step
print('error add digital flow sensor:%d' % error)

# tested
data_sens=c_double()
#set_channel=input("select channel(1-4) : ")
set_channel=3
set_channel=int(set_channel) #convert to int
set_channel=c_int32(set_channel) #convert to c_uint32
for i in range(5):
    time.sleep(1.0) #
    error=M_S_R_D_Get_Sens_Data(Instr_ID,set_channel.value,byref(data_sens))
    time.sleep(0.5) #
    print('Press or Flow ch', set_channel.value,': ',data_sens.value)
    print( 'error :', error)