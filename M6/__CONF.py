#
#   TwoGuysOneWorkshop
#   simCNC configuration
#   2023-05-25 / André 
#


#-----------------------------------------------------------
# Ports & Pins 
#-----------------------------------------------------------

out_opencollet      = 10
out_cleancone       = 12
out_curtain         = 14
out_vac             = None

in_colletclosed     = 10
in_colletopened     = 10
in_toolinside       = 8
in_pressure         = 5
in_curtain_up       = None

in_probe_wcs_signal = 0
in_probe_wsc_error  = 0
in_probe_tool_signal= 0

#-----------------------------------------------------------
# ATC
#-----------------------------------------------------------

# positions
pos_atc_z_toolget   = -115.450      # Z position of tools if not defined different
pos_atc_z_purge			 = -80
pos_atc_pockets     = {1: {'X': 100, 'Y': 100, 'Z': -100} }

# moving
move_atc_z_safe     = -20
move_atc_z_clean    = 10
move_atc_xslide     = 75
move_atc_safe_x     = 250           # safe position in X to move with tool in spindle 

feed_atc_z_final    = 800
feed_atc_z_fast     = 2500
feed_atc_xy         = 2500 

# config
conf_atc_purge_time = 0.5           # purge time in sec
conf_tools_special  = {0}           # No automatic tool change 
conf_tools_noprobe  = {0,10}        # No automatic length probing 
conf_tools_count    = 10            # range considered for automatic change, rest will call for manual 

#-----------------------------------------------------------
# Probing - WCS
#-----------------------------------------------------------

conf_probe_wcs_active   = None      # active?
conf_probe_wcs_index    = 0         # CSMIO probe ID

# wakeup
conf_probe_wcs_wakeup   = True      # wake up yes/no?
conf_probe_wcs_wakerpm  = 1000      # wake up RPM for probe
conf_probe_wsc_wake_t   = 5         # seconds to run spindle 

#-----------------------------------------------------------
# Probing - Tools
#-----------------------------------------------------------

conf_probe_t_active   = None        # active?
conf_probe_t_index    = 0           # CSMIO probe ID
conf_probe_t_pos      = {'X': 100, 'Y': 100, 'Zstart': -50, 'Zend': -100}

#-----------------------------------------------------------
# Axis allocation
#-----------------------------------------------------------

X = 0
Y = 1
Z = 2
A = 3
C = 5