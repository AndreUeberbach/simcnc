#
#   TwoGuysOneWorkshop
#   simCNC macro M6 tool change
#   2023-05-25 / André 
#

from ___CONFIG import * 
import time   
import sys

timezone = time.localtime() 



mode = "debugx" 



msg_air_warning         = "ERR - ATC - air pressure too low"
msg_clamp_error         = "ERR - ATC - Clamp could not be opened"
msg_clamp_error_close		= "ERR - ATC - Clamp could not be closed"
msg_spindle_error       = "ERR - ATC - Spindle still spinning" 
msg_old_equal_new       = "INF - ATC - New tool equal to old tool. M6 aborted"
msg_tool_out_range      = "ERR - ATC - Selected tool out of range"
msg_tool_unload_error   = "ERR - ATC - Could not unload tool"
msg_tool_load_error			= "ERR - ATC - Could not load tool" 
msg_ref_error           = "ERR - ATC - Axis not referenced"
msg_tool_zero           = "ERR - ATC - Tool zero cannot be called"
msg_tool_count          = "ERR - ATC - Tool number out of range"
msg_tool_special					= "ERR - ATC - Special tool, no ATC available"

#-----------------------------------------------------------
# Check status of pin 
#-----------------------------------------------------------

# Get digital input pin status
def getPinStatus(pin_in):

        csmio = d.getModule(ModuleType.IP, 0) 

        if pin_in is None: #ignore 
            return None

        if csmio.getDigitalIO(IOPortDir.InputPort, pin_in) == DIOPinVal.PinSet: 
            return True
        else:
            return False 
        
# Get digital output pin status
def setOutput(pin_out, state):
    
    if state == True: state2 = DIOPinVal.PinSet
    if state == False: state2 = DIOPinVal.PinReset

    if pin_out is None: # ignore "none"
        return None
    try:
        csmio = d.getModule(ModuleType.IP, 0)
        csmio.setDigitalIO(pin_out, state2)
    except NameError:
        print(_("------------------\nDigital Out defined wrong"))

# Throw message and end program 
def throwMessage(message, action):

    ttime = time.strftime("%H:%M:%S", timezone)
    print("\n"  + ttime + " - " + message)

    if message == True: 
        
        msg.info("\n"  + ttime + " - " + message)
				
    if action == "exit":
        sys.exit(0)
        

#-----------------------------------------------------------
# Prep
#-----------------------------------------------------------

tool_old_id     =  d.getSpindleToolNumber()
tool_new_id     =  d.getSelectedToolNumber()
tool_new_len    =  d.getToolLength(tool_new_id)
machine_pos     =  d.getPosition(CoordMode.Machine)


if mode == "debug":
	print(f"{tool_old_id}  -> {tool_new_id}")


# ignore softlimits
d.ignoreAllSoftLimits(True)

# Spindle off
d.setSpindleState(SpindleState.OFF)



#-----------------------------------------------------------
# Start M6
#-----------------------------------------------------------
 
# check air pressure
if getPinStatus(in_pressure) == False:  
    throwMessage(msg_air_warning, "exit")

# exit if tool is already in spindle 
if tool_old_id == tool_new_id: 
    throwMessage(msg_old_equal_new, "exit")

# exit on tool zero
if tool_new_id == 0: 
    throwMessage(msg_tool_zero, "exit") 

if tool_new_id > conf_tools_count:
    throwMessage(msg_tool_count, "exit") 	 

# Curtain up 
setOutput(out_curtain, True)

# move safe z  
machine_pos[Z] =  move_atc_z_safe
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)


# if tool in spindle, go and drop 
if getPinStatus(in_toolinside) == True:   #inverted!

	machine_pos[Y] =  10
	d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

	machine_pos[X] = pos_atc_pockets[1]['X'] + move_atc_xslide
	d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

	machine_pos[Y] = pos_atc_pockets[1]['Y']
	d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

	machine_pos[Z] = pos_atc_pockets[1]['Z']
	d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

	machine_pos[X] = pos_atc_pockets[1]['X']
	d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

	setOutput(out_opencollet, True)
	time.sleep(1)

	# if clamp does not open
	if getPinStatus(in_colletopened) == False:
		throwMessage(msg_clamp_error, "exit")

	machine_pos[Z] =  move_atc_z_safe
	d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)		
	
	time.sleep(1)

	setOutput(out_opencollet, False)


## fetch next tool 
machine_pos[Y] =  pos_atc_pockets[1]['X']
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

setOutput(out_opencollet, True)

machine_pos[Z] = pos_atc_z_purge
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

setOutput(out_cleancone, True)

machine_pos[Z] = pos_atc_pockets[1]['Z']
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

setOutput(out_cleancone, False)
setOutput(out_opencollet, False)

time.sleep(1)

# if clamp is not closed
if getPinStatus(in_colletclosed) == False:
	throwMessage(msg_clamp_error_close, "exit")

machine_pos[X] = pos_atc_pockets[1]['X'] + move_atc_xslide
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

machine_pos[Z] =  move_atc_z_safe
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)

# if no tool
if getPinStatus(in_toolinside) == False:
	throwMessage(msg_tool_load_error, "exit")

#-----------------------------------------------------------
# End M6
#-----------------------------------------------------------

setOutput(out_curtain, False)