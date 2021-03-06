import re
import sys,time
from ctypes import *

from Elveflow64 import MUX_Destructor,MUX_Initialization,MUX_Set_all_valves,MUX_Get_Trig,MUX_Set_Trig,MUX_Set_indiv_valve,MUX_Wire_Set_all_valves



"""
python wrapper for Multiplexer to control Valves connected by wires, 
supported max 16 channel, 
for valve 6712type
0 is Low (0V) -> valve open
1 is High(5V) -> valve close 
"""

class Multiplexer(object):
    """Elveflow Multiplexer for valve control
    provide A connected instrument name(by NI MAX tool) and initialize before further usage
    Args:
        Name: The name of the instrument by NI MAX tool

    """
    
    def __init__(self,name=None):
        super(Multiplexer, self).__init__()
        self.MuxName = name.encode('ascii')
        self.Mux_ID=c_int32()
    
    def initialize_MUX(self):
        """initialize the Multiplexer
        returns the ID number of the Multiplexer
        
        Args:
            Name: name of the Multiplexer from NI MAX tool
        returns:
            tuple: error,Mux_ID
        """
        error=MUX_Initialization(self.MuxName,byref(self.Mux_ID))
        # error=0 if initialization succeeded with Mux_ID>0 ,else return error,Mux_ID=-1
        return error, self.Mux_ID.value
    
    def Mux_set_Trigger(self,trigger:int):
        """set trigger 
        return error=0 if set trigger succeeded
        
        Args:
            trigger (int): 0 is 0V,1 is 5V
        Returns:
            tuple: error,trigger
        """
        mux_trig=c_int32(trigger)
        error=MUX_Set_Trig(self.Instr_ID,mux_trig)
        return error,trigger  
    
    def Mux_get_Trigger(self):
        """get trigger
        0 is 0V,1 is 5V
        
        Returns:
            tuple: error,trigger
        """
        trigger=c_int32()
        error=MUX_Get_Trig(self.Mux_ID,byref(trigger))
        return error,trigger.value

    def MuxWire_setAll_valves(self,valves_array:list=[0]*16):
        """set all Wired valves 0-16
        specific for MUX Wire instrument, supported maxmal 16 channel
        length of valves_array should be exactly 16 with int=(0 or 1)
        error is 0 if succeed
        
        Args:
            valves_array (list): list of 16 int (0 or 1) for all 0-15 channels
        Returns:
            tuple:error,valve_array
        """
        valve_state=(c_int32*16)(0)
        error=-1
        if valves_array:
            if len(valves_array)==16:
                for index,val in enumerate(valves_array):
                    valve_state[index] = c_int32(val)
                error=MUX_Wire_Set_all_valves(self.Mux_ID,valve_state,16)
        return error,valves_array

    def set_all_valves(self,valves_array:list=[0]*16):
        """set all valves
        specific for MUX flow switch instrument,
        open or closed, 16 channels supported
        
        Args:
            valves_array (list): list of 16 int (0 or 1) for all 0-15 channels
        Returns:
            tuple:error,valve_array[list]
        """
        valve_state=(c_int32*16)(0)
        error=-1
        if valves_array:
            if len(valves_array)==16:
                for index,val in enumerate(valves_array):
                    valve_state[index] = c_int32(val)
                error=MUX_Set_all_valves(self.Mux_ID,valve_state,16)
        return error,valves_array

    def set_indiv_valve(self,valve_in:int,valve_out:int,state:int):
        """set the state of one value
        specific for MUX cross chip only ,
        0 is closed, 1 is open
        Args:
            valve_channel (int): channel number for this value
            state (int): 0 is close, 1 is open
        """
        error=MUX_Set_indiv_valve(self.Mux_ID,c_int32(valve_in),c_int32(valve_out),c_int32(state))
        return error
    
    def close_Mux(self):
        """close the communication to the multiplexer
        Return 0 if successful
        """
        error=MUX_Destructor(self.Instr_ID)
        return error

if __name__=="__main__":
    # bulid one multiplexer with name from NI MAX tool
    Mux_valve=Multiplexer(name='Dev2')
    error_init,Mux_ID=Mux_valve.initialize_MUX()
    print(f'Fluidic valve controller initialized with error: {error_init} and ID: {Mux_ID}')
    error_trig,trigger=Mux_valve.Mux_get_Trigger()
    print(f'error_trig: {error_init} and trigger: {trigger}')
    valve_state_off=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    valve_state_on=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    time.sleep(0.5)
    # for valves use MuxWire_setAll_valves
    error_set,valve_list=Mux_valve.MuxWire_setAll_valves(valve_state_off)
    print(f'set all valves with error: {error_set}, valve_list: {valve_list}')
    # close communication
    error_close=Mux_valve.close_Mux()
    print(f'close multiplexer with error:{error_close},0 means OK')