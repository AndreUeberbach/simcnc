#
#   TWO GUYS, ONE WORKSHOP 
#   http://cnc.a-ueberbach.de/
#
#   simCNC file explorer alternative
#
#   Disclaimer. This is open source code and the author shall not be held responsible for any damages, injuries or losses.
#   Use this code at your own risk and make sure you adjust it to your machine properly.
#
#   2023-06-28 / André Ueberbach 
#   v0.5 2023-06-28
#

######################################################## 
#############  IMPORT & SETUP

import time 
import sys
import pathlib
import os
import re
import fileinput

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

timezone = time.localtime() 
folder_path = "/Users/aueberbach/Dropbox/CNC-Austausch/n-NC Programme"	# define path to be loaded. Currently static! 
accepted_ftype = ".nc" # define file type to be displayed



#####

fileSelected = "" #global var to buffer current selection from event 

######################################################## 
#############  FUNCTIONS 


# ----------------------------------------
# Event handler for treeView
#
def on_click(self, event):
    tree = event.widget
    item_name = tree.identify_row(event.y)
    if item_name:
        tags = tree.item(item_name, 'tags')
        if tags and (tags[0] == 'selectable'):
            tree.selection_set(item_name)
            msg.info(item_name)

# ----------------------------------------
# Get last modification timestamp of file
#
def get_last_modification_time(file_path):
    if os.path.exists(file_path):
        timestamp = os.path.getmtime(file_path)
        last_modified = time.strftime('%H:%M %d.%m.%Y', time.localtime(timestamp))
        return last_modified
    else:
        return "File not found."

# ----------------------------------------
# Load first 30 lines of a file
#
def load_file_50_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        first_50_lines = ''.join(lines[:50])
        return first_50_lines


# ----------------------------------------
# Count number of lines of given file
#
def count_lines(file_path):
    line_count = 0
    with fileinput.input(files=file_path) as file:
        for line in file:
            line_count += 1
    return line_count



# ----------------------------------------
# Alternative function to extract_gcode_info, in case standard PP is used and file info is not added in header
#
def findTools(path):
	tool_numbers = []
	thisReturn = []
	lcount = 0

	with open(path, 'r') as file:		
		for line in file:
			lcount = lcount + 1
			if line.startswith("T"):
				tool_number = line.split(" ")[0][1:]
				tool_numbers.append(str(tool_number))
		
		thisReturn.append(lcount)
		thisReturn.append(tool_numbers)
		return thisReturn

# ----------------------------------------
# Event handler for treeView on-focus
#
def loadGCodeFile(a):

	global fileSelected

	curItem = tree.focus()
	curItem = tree.item(curItem)

	fileSelected  = curItem['text']
	
# ----------------------------------------
# "open" button action
#
def openButton():

	global fileSelected 
	global folder_path
	
	print(f"--> Opening {folder_path}/{fileSelected}")

	if fileSelected  != "":
		d.openGCodeFile(f"{folder_path}/{fileSelected}")
		root.destroy()

#root.loadGCodeFile(folder_path + "/" + "bla.nc")

# ----------------------------------------
# Get information about stock, comment, work coordinate system, program id and used tools from GCode file
#
def extract_gcode_info(gcode):

		# patterns to fetch the information
    program_id_pattern = r"\(O(\d+)\s*(.*?)\)"   # program_id_pattern = r"\(O(\d+)\)"
    stock_size_pattern = r"STOCK SIZE X([\d.]+) Y([\d.]+) Z(\d+)"
    tool_pattern = r"\(T(\d+)\s*D=(\d+)\.\s+CR=(\d+)\.\s+-\s+ZMIN=(-?\d+)\.\s+-\s+(.+?)\)"
    wcs_pattern = r"WCS\s+(G\d+)"

    program_id = re.search(program_id_pattern, gcode)
    stock_size = re.search(stock_size_pattern, gcode)
    tools = re.findall(tool_pattern, gcode)
    wcs_numbers = re.findall(wcs_pattern, gcode)


		# list initiation
    result = {}
    result['stock'] = ""
    result['comment'] = ""
    result['wcs'] = ", ".join(wcs_numbers)
    result['id'] = ""
    result['tools'] = {}


		# if program ID was found
    if program_id:
        result['id'] = program_id.group(1)
        result['comment'] = program_id.group(2)
    else:
        result['id'] = "-"
        result['comment'] = "-"

		# if stock size was found
    if stock_size:
        stock_x = float(stock_size.group(1))
        stock_y = float(stock_size.group(2))
        stock_z = int(stock_size.group(3))	

        result['stock'] = f'{stock_x} x {stock_y} x {stock_z}'
    else:
        result['stock'] = "-"


    toolCount = 0

		# loop tools 
    for tool in tools:
	
        toolCount = toolCount + 1
        result['tools'][toolCount] = {"concat":  f"#{tool[0]} / d={tool[1]}mm / {tool[4]}","number": tool[0], "diameter": tool[1], "name": tool[4], "zmin": tool[3], "cr": tool[2]}

    return result



######################################################## 
#############  LOGIC / VISUALIZATION 

# create tk window
root = tk.Tk()
root.title('GCode File Explorer')

# remove title bar... nice little tweak :)
root.overrideredirect(True)
root.overrideredirect(False)

w = 690 # Width 
h = 600 # Height
 
screen_width = root.winfo_screenwidth()  # Width of the screen
screen_height = root.winfo_screenheight() # Height of the screen
 
# Calculate Starting X and Y coordinates for Window
x = (screen_width/2) - (w/2)
y = (screen_height/2) - (h/2)
 
root.geometry('%dx%d+%d+%d' % (w, h, x, y))  # center on screen

# hide title bar
#root.overrideredirect(True)

# configure the grid layout
root.rowconfigure(0)
root.columnconfigure(0)
root.rowconfigure(1, weight=1)
root.columnconfigure(1, weight=1)
root.configure(bg='#2D2D2D')


# configure and setup buttons 
style = ttk.Style(root)

style.configure('Custom.TLabel', font =
            ('calibri', 16),
                borderwidth = '3', 
					padding=4,
					background='#707070', foreground='gray', focuscolor='#707070', relief='flat')


close_button = ttk.Button(root, text='Close', command=root.destroy, style = 'Custom.TLabel').grid(row=0, column=0, ipady=5, ipadx=5, pady=5, padx=5, sticky="w")
open_button = ttk.Button(root, text='Open selected', style='Custom.TLabel', command=lambda: openButton()).grid(row=0, column=2, ipady=5, ipadx=5, pady=5, padx=5)


# create the treeview and apply a bit of stlying
tree = ttk.Treeview(root, columns=('info')) #, selectmode='none')
tree['columns'] = ('date', 'time')


style.configure('Treeview', rowheight=40)

style.configure("Treeview", background="#2D2D2D", 
                fieldbackground="#2D2D2D",
								foreground="white", relief='flat', borderwidth='0')
style.map('Treeview', background=[('selected', '#707070')])  # color code selected item 


tree.heading('#0', text=f' ', anchor=tk.W)
tree.bind('<ButtonRelease-1>', loadGCodeFile)


#colors
tree.tag_configure('selected', background='yellow')
tree.tag_configure('g', background='#86b02c')
tree.tag_configure('y', background='#2c44b0')
tree.tag_configure('r', background='#f58484')
tree.tag_configure('odd', background='#333333')
tree.tag_configure('even', background='#2D2D2D')
tree.tag_configure('filename', font=(None, 18))


tree.column('date', width=40, anchor='e')
tree.column('time', width=20, anchor='e')

tree.heading('time', text='Date')
tree.heading('date', text='Time')

# adding data
tree.insert('', tk.END, text=f'USB Drive [disabled]', iid=0, open=False, tags=('g','filename', 'even'))
tree.insert('', tk.END, text=f'{folder_path}', iid=1, open=True, tags=('g','filename', 'even'))

# images
self_dir = pathlib.Path(__file__).parent.resolve()

img_watch = tk.PhotoImage(file=f"{self_dir}/ico/watch_sml.png")
img_endmill = tk.PhotoImage(file=f"{self_dir}/ico/endmill_sml.png")
img_info= tk.PhotoImage(file=f"{self_dir}/ico/info_sml.png")
img_wcs= tk.PhotoImage(file=f"{self_dir}/ico/wcs_sml.png")
img_stock= tk.PhotoImage(file=f"{self_dir}/ico/stock_sml.png")


treeID = 2

# List all files in the folder
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Filter files with .tap or tap extension
nc_files = [f for f in files if f.endswith(accepted_ftype)]

# loop files in folder
for file in nc_files:

	thisFile = folder_path + "/" + file
	tpos = 0

	# get first 30 lines of each file and extract tool/stock/wcs/comment information
	lines = load_file_50_lines(thisFile)
	data = extract_gcode_info(lines)

	# get some general file info
	f_mod = get_last_modification_time(thisFile)
	f_lines = count_lines(thisFile)
	toolCount = len(data['tools']) 

	# intermediate step, as f-string will not allow direct access... grrr
	f_comment = data['comment']
	f_stock = data['stock']
	f_wcss = data['wcs']


	tags = "odd" # set tag for color coding row. Preparation for banded rows at a later stage
	
	# populate treeView 
	tree.insert(1, tk.END, text=f'{file}', iid=treeID, open=False, tags=('filename', 'selectable'), values=(f'{f_mod}'))
	
	tree.insert(treeID, tk.END, text=f'{f_mod}', iid=(treeID + 1), open=True, tags=tags, values='')	# time/date last modified
	tree.insert(treeID, tk.END, text=f'  {f_comment}', iid=(treeID + 2), open=True, tags=tags, values='', image=img_info) # PP comment
	tree.insert(treeID, tk.END, text=f'  Lines: {f_lines}', iid=(treeID + 3), open=True, tags=tags, values='', image=img_watch) #file line count
	tree.insert(treeID, tk.END, text=f'  WCS: {f_wcss}', iid=(treeID + 4), open=True, tags=tags, values='', image=img_wcs) # used work coordinate systems (wcs)
	tree.insert(treeID, tk.END, text=f'  Stock: {f_stock} mm', iid=(treeID + 5), open=True, tags=tags, values='', image=img_stock) # stock size from PP comments
	tree.insert(treeID, tk.END, text=f'  Tool(s): {toolCount}', iid=(treeID + 6), open=True, tags=tags, values='', image=img_endmill) # tools used

	# if more than 0 tools, loop tools and add to treeView
	if toolCount > 0:
		for tool in data['tools']:

			tree.insert((treeID + 6), tk.END, text=data['tools'][tool]['concat'], iid=(treeID + 6 + 1 + tool), open=True, tags=tags, values='', image=img_endmill) # tools used

	treeID = treeID + 8 + len(data['tools'])


# place the Treeview widget on the root window
tree.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)



# run the app
root.mainloop()