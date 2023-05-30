#
#   TWO GUYS, ONE WORKSHOP 
#   http://cnc.a-ueberbach.de/
#
#   simCNC import function for Autodesk Fusion360 tool library (json format)
#
#   Disclaimer. This is open source code and the author shall not be held responsible for any damages, injuries or losses.
#   Use this code at your own risk and make sure you adjust it to your machine properly.
#
#   All configurations and settings are done in file ___CONF.py
#
#   2023-05-25 / André Ueberbach 
#   v1.3 2023-05-27
#



## ATTENTION - WORK IN PROGRESS - FIRST PROOF OF CONCEPT ONLY ##


import sys
import time
import json

timezone = time.localtime() 

tools_number_start = 1
tools_number_end = 16
sim_tools_flush = True

tool_parameter_create = True 
tool_parameter_name_start = 1000 # custom parameter range to store tool names

msg_resetalltools = "Do you want to reset all tool table data?"
msg_notopened = "ERR - Import - Could not open file "
msg_wrongfile = "ERR - Import - File does not theme a Fusion360 tool JSON"
msg_count = "INF - Import - Number of tools to be imported: "
msg_range = "ERR - Import - Number of tools to be imported greater than range"
msg_maxrange = "ERR - Import - Number of tools must be max. 255"

#-----------------------------------------------------------
# Functions 
#-----------------------------------------------------------

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION to flush the tool table from all entries
# Args: message(string), action(boolean)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def flushToolTable(tool_number_start, tool_number_end):
    for tool_number in range(tool_number_start, tool_number_end):
        d.setToolLength(tool_number, 0)
        d.setToolDiameter(tool_number, 0)
        d.setToolDiameterWear(tool_number, 0)

#-----------------------------------------------------------
# Import 
#-----------------------------------------------------------

# open json file 

try: 
    with open('/Users/aueberbach/Dropbox/CNC-Austausch/x-simcnc/fusion360 integration/Holz.json', 'r') as f:
        data = json.load(f)
except IOError as e:
    throwMessage(msg_notopened + " -> ({0}): {1}".format(e.errno, e.strerror), "exit")
except:
    throwMessage(msg_notopened + " -> " + sys.exc_info()[0], "exit")


#-----------------------------------------------------------
# Perform pre-checks
#-----------------------------------------------------------

# exit if file does not theme to be a Fusion360 JSON file 
if not data["data"]:
    throwMessage(msg_notopened, "exit")

# output tool file content count
import_count = len(data["data"])
throwMessage(msg_count + str(import_count), "")

# check if tool range is available 
if sim_tools_flush == True and import_count > (tools_number_end - tools_number_start):
    throwMessage(msg_range, "exit")    

if import_count > 255: 
    throwMessage(msg_maxrange, "exit")           

# Flush all tools currently in table?
if sim_tools_flush == True: 
    flushToolTable(tools_number_start, tools_number_end)

#-----------------------------------------------------------
# IMPORT 
#-----------------------------------------------------------

# loop through tools and fetch data 
for line, _tool in enumerate(data["data"]):
    t_descr = _tool["description"]
    t_type = _tool["type"]
    t_number = _tool["post-process"]["number"]
    t_diameter = _tool["post-process"]["diameter-offset"]
    t_length = _tool["post-process"]["length-offset"]
    #t_coolant = _tool["start-values"]["presets"]["tool-coolant"]

    print("     " + str(line + 1) + " --> #" + str(t_number)  + " / descr:" + str(t_descr) + " / type:" + str(t_type) + " / dia:" + str(t_diameter)  + " / len:" + str(t_length)  + "/n")

    tool_number = (line +1)
    d.setToolLength(tool_number, t_length)
    d.setToolDiameter(tool_number, t_diameter)

    if tool_parameter_create == True:
        d.setMachineParam((tool_parameter_name_start + tool_number), tool_number) # create custom parameter to store tool position in magazine 