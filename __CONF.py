#
#   TwoGuysOneWorkshop
#   simCNC configuration
#   2023-05-25 / André 
#


#-----------------------------------------------------------
# Ports & Pins 
#-----------------------------------------------------------

out_opencollet      = 10        # open spindle tool clamping
out_cleancone       = 12        # activate cone cleaning / purging
out_curtain         = 14        # move dust hood / curtain up
out_vac             = None      # enable vacuum 

in_colletclosed     = 10        # spindle: clamping closed
in_colletopened     = 10        # spindle: clamping opened
in_toolinside       = 8         # spindle: tool inside cone 
in_pressure         = 5         # pressure switch (active when ok)
in_curtain_up       = None      # dust hood / curtain in safe (up) position

in_probe_wcs_signal = 0         # probe active signal (wcs)
in_probe_wsc_error  = 0         # probe error signal (wcs)
in_probe_tool_signal= 0         # probe active signal (tool length)

#-----------------------------------------------------------
# ATC
#-----------------------------------------------------------

# positions
pos_atc_z_toolget   = -115.450      # Z position of tools if not defined different
pos_atc_z_purge		= -80           # Position at which purging is activated
pos_atc_pockets     = {1: ['X': 100, 'Y': 100, 'Z': -100], 2: ['X': 100, 'Y': 100, 'Z': -100]}

# moving
move_atc_z_safe     = -20
move_atc_z_clean    = 10
move_atc_xslide     = 75
move_atc_safe_x     = 250           # safe position in X to move with tool in spindle 
move_atc_safe_y     = 20            # safe position in Y to move to tool magazine 

feed_atc_z_final    = 800           # Z feed before reaching tool
feed_atc_z_fast     = 2500          # Z feed general
feed_atc_xy         = 2500          # XY feed in general 

# config
conf_atc_purge_time = 0.5           # purge time in sec
conf_tools_special  = {0}           # No automatic tool change 
conf_tools_noprobe  = {0,10}        # No automatic length probing 
conf_tools_count    = 10            # range considered for automatic change, rest will call for manual 
conf_pause_debounce = 0.5           # debounce time for tool clamp close before checking sensor

#-----------------------------------------------------------
# Probing - WCS
#-----------------------------------------------------------

conf_probe_wcs_active   = None      # active?
conf_probe_wcs_index    = 0         # CSMIO probe ID

# wakeup
conf_probe_wcs_wakeup   = True      # wake up yes/no?
conf_probe_wcs_wakerpm  = 1000      # wake up RPM for probe
conf_probe_wsc_wake_t   = 5         # seconds to run spindle 

# probe 
conf_probe_wcs_len      = 0         # probe length
conf_probe_wcs_dia      = 0         # probe diameter
conf_probe_wcs_slag     = 0         # probe dead-way / slag 

# probing 
conf_probe_wcs_feed_fst = 500       # fast probing speed
conf_probe_wcs_feed_slo = 100       # slow probing speed
conf_probe_wcs_do_fine  = True      # perform fine probing  

#-----------------------------------------------------------
# Probing - Tools
#-----------------------------------------------------------

conf_probe_t_active   = None        # active?
conf_probe_t_index    = 0           # CSMIO probe ID
conf_probe_t_pos      = {'X': 100, 'Y': 100, 'Zstart': -50, 'Zend': -100} # Position of probe

#-----------------------------------------------------------
# Axis allocation
#-----------------------------------------------------------

X = 0
Y = 1
Z = 2
A = 3
C = 5