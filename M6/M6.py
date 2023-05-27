#
#   TWO GUYS, ONE WORKSHOP 
#   http://cnc.a-ueberbach.de/
#
#   simCNC macro M6 tool change for a tool magazine along side the Y axis
#   Inspired by Erwan Le Foll (erwan56450)
#
#   Disclaimer. This is open source code and the author shall not be held responsible for any damages, injuries or losses.
#   Use this code at your own risk and make sure you adjust it to your machine properly.
#
#   All configurations and settings are done in file ___CONF.py
#
#   2023-05-25 / André Ueberbach 
#   v1.3 2023-05-27
#

from ___CONF import * 
import time   
import sys

timezone = time.localtime() 

mode = "debug" # normal or debug (for more info output)

#-----------------------------------------------------------
# Check status of pin 
#-----------------------------------------------------------

msg_air_warning         = "ERR - ATC - air pressure too low"
msg_clamp_error         = "ERR - ATC - Clamp could not be opened"
msg_clamp_error_close	= "ERR - ATC - Clamp could not be closed"
msg_spindle_error       = "ERR - ATC - Spindle still spinning" 
msg_old_equal_new       = "INF - ATC - New tool equal to old tool. M6 aborted"
msg_tool_out_range      = "ERR - ATC - Selected tool out of range"
msg_tool_unload_error   = "ERR - ATC - Could not unload tool"
msg_tool_load_error     = "ERR - ATC - Could not load tool" 
msg_ref_error           = "ERR - ATC - Axis not referenced"
msg_tool_zero           = "ERR - ATC - Tool zero cannot be called"
msg_tool_count          = "ERR - ATC - Tool number out of range"
msg_tool_special        = "ERR - ATC - Special tool, not available for auto tool change"
msg_tool_dropoff        = "OK - ATC - Old tool dropped off"
msg_m6_end              = "OK - ATC - M6 successful"
msg_noprobe             = "INFO - ATC - Tool probing aborted, tool number in exception list"

#-----------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION to GET status of IO pin
# Args: pin_in(int)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getPinStatus(pin_in):

    csmio = d.getModule(ModuleType.IP, 0) 

    if pin_in is None: #ignore 
        return None

    if csmio.getDigitalIO(IOPortDir.InputPort, pin_in) == DIOPinVal.PinSet: 
        return True
    else:
        return False 
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION to SET status of IO pin
# Args: pin_out(int), state(boolean)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION to throw message in py status line and optionally end program 
# Args: message(string), action(boolean)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

# Store some info for later use
tool_old_id     =  d.getSpindleToolNumber()
tool_new_id     =  d.getSelectedToolNumber()
tool_new_len    =  d.getToolLength(tool_new_id)
machine_pos     =  d.getPosition(CoordMode.Machine)


# if debug is enabled, output some helpful information
if mode == "debug":
    print(f"{tool_old_id}  -> {tool_new_id}")

#-----------------------------------------------------------
# Perform pre-checks
#-----------------------------------------------------------
 
# exit if tool is in exception list for auto-tool-change 
if tool_new_id in conf_tools_special:
    throwMessage(msg_tool_special, "exit")   

# exit if air pressure is too low 
if getPinStatus(in_pressure) == False:  
    throwMessage(msg_air_warning, "exit")

# exit if tool is already in spindle
if tool_old_id == tool_new_id: 
    throwMessage(msg_old_equal_new, "exit")

# exit on tool zero
if tool_new_id == 0: 
    throwMessage(msg_tool_zero, "exit") 

# exit if tool is out of range
if tool_new_id > conf_tools_count:
    throwMessage(msg_tool_count, "exit") 	 


#-----------------------------------------------------------
# Prepare
#-----------------------------------------------------------

# ignore softlimits
d.ignoreAllSoftLimits(True)

# Spindle off
d.setSpindleState(SpindleState.OFF)

# Curtain up 
setOutput(out_curtain, True)

# move to safe Z 
machine_pos[Z] =  move_atc_z_safe
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)

# move to Y start position
machine_pos[Y] = move_atc_safe_y
d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)


#-----------------------------------------------------------
# If tool is present in spindle
#-----------------------------------------------------------

# if a tool is in spindle, go and drop that first 
if getPinStatus(in_toolinside) == True:   #inverted on my machine!

    # move to X position of tool + xslide value 
    machine_pos[X] = pos_atc_pockets[tool_old_id]['X'] + move_atc_xslide
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

    # move to Z- position of tool
    machine_pos[Z] = pos_atc_pockets[tool_old_id]['Z']
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)

    # slide tool in pocket (X-)
    machine_pos[X] = pos_atc_pockets[tool_old_id]['X']
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

    # Open spindle clamping
    setOutput(out_opencollet, True)
    time.sleep(conf_pause_debounce)

    # exit if clamp does not open
    if getPinStatus(in_colletopened) == False:
        throwMessage(msg_clamp_error, "exit")

    # move to safe Z
    machine_pos[Z] =  move_atc_z_safe
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)		
	
    time.sleep(1)

    # close clamping and write message 
    setOutput(out_opencollet, False)
    throwMessage(msg_tool_dropoff, "")


#-----------------------------------------------------------
# Fetch new tool
#-----------------------------------------------------------

## fetch new tool, if a number > 0 was selected
if tool_new_id > 0: 

    # move to X position of tool
    machine_pos[X] = pos_atc_pockets[tool_new_id]['X']
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

    # move to Y position of tool 
    machine_pos[Y] =  pos_atc_pockets[tool_new_id]['Y']
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

    # open clamping
    setOutput(out_opencollet, True)

    # check if clamping is open
    if getPinStatus(in_colletopened) == False:
        throwMessage(msg_clamp_error, "exit")

    # move to Z- height where spindle cone cleaning is activated
    machine_pos[Z] = pos_atc_z_purge
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)

    # activate spindle cone cleaning
    setOutput(out_cleancone, True)

    # move to Z- of tool
    machine_pos[Z] = pos_atc_pockets[tool_new_id]['Z']
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_final)

    # close clamp and deactivate cone cleaning
    setOutput(out_cleancone, False)
    setOutput(out_opencollet, False)

    time.sleep(conf_pause_debounce)

    # exit if clamp is not closed
    if getPinStatus(in_colletclosed) == False:
        throwMessage(msg_clamp_error_close, "exit")

    # exit if no tool was picked up 
    if getPinStatus(in_toolinside) == False:
        throwMessage(msg_tool_load_error, "exit")

    # slide tool out X+ + slideout
    machine_pos[X] = pos_atc_pockets[tool_new_id]['X'] + move_atc_xslide
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_xy)

    # move to Z safe 
    machine_pos[Z] =  move_atc_z_safe
    d.moveToPosition(CoordMode.Machine, machine_pos, feed_atc_z_fast)

#-----------------------------------------------------------
# Tool length probing?
#-----------------------------------------------------------

# call tool length probing if enabled 
if conf_probe_t_active != None:
    
    # exit if tool is in no_probe_list 
    if conf_tools_noprobe[tool_new_id]: 
        throwMessage(msg_noprobe, "")
    else: 
        throwMessage(msg_calling_probing, "")
        # call probing 

#-----------------------------------------------------------
# Finish up and provide information to simCNC 
#-----------------------------------------------------------

# Set new tool in simCNC 
d.setToolLength (tool_new_id, tool_new_length)
d.setToolOffsetNumber(tool_new_id)
d.setSpindleToolNumber(tool_new_id)

# lower curtain and send success message 
setOutput(out_curtain, False)
throwMessage(msg_m6_end, "")