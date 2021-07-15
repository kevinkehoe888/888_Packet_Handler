from tkinter import *
from tkinter import filedialog
from tkcalendar import DateEntry
import paramiko
import time
from datetime import date, datetime, timedelta
import os
import tarfile
import re
import shutil
import threading
import tempfile
import binascii
import atexit
from stat import S_ISDIR, S_ISREG
import json

# How to build
# pyinstaller --onefile --hidden-import babel.numbers --windowed 888_Packet_Handler.py

root = Tk()
root.title("888 Packet Handler")
root.geometry("1300x750")

supplier_options = [
  "lsport - LSports",
  "sportradar - SportRadar",
  "METRIC - Metric Gaming",
  "AT_THE_RACES - At The Races",
  "RACING_UK - Racing UK",
  "SIS - SPIN Horse Racing",
  "CMT - CMT",
  "PA - Press Association",
  "PAGH - Dogs",
  "BR - BetRadar",
  "BRIN - BetRadar Inplay",
  "SSOL - Sporting Solutions",
  "SSOLIN - Sporting Solutions InPlay",
  "BGIN - BetGenius",
  "BGIN_SC - BetGenius_SC"
]

supplier_local_folders= [
  ["LSports_Packet_Folder"],
  ["Sportrader_Packet_Folder"],
  ["Metric_Packets_from_400", "Metric_Packets_from_64c"],
  ["ATR_Packets_from_1e5", "ATR_Packets_from_cbe", "ATR_Packets_from_bdc", "ATR_Packets_from_143", "ATR_Packets_from_3fc", "ATR_Packets_from_3c1", "ATR_Packets_from_b48", "ATR_Packets_from_bf6"],
  ["RUK_Packets_from_1e5", "RUK_Packets_from_cbe", "RUK_Packets_from_bdc", "RUK_Packets_from_143", "RUK_Packets_from_3fc", "RUK_Packets_from_3c1", "RUK_Packets_from_b48", "RUK_Packets_from_bf6"],
  ["SIS_Packets_from_1e5", "SIS_Packets_from_cbe", "SIS_Packets_from_bdc", "SIS_Packets_from_143", "SIS_Packets_from_3fc", "SIS_Packets_from_3c1", "SIS_Packets_from_bf6"],
  ["CMT_Packets_from_cbe"],
  ["PA_Packets_from_bdc"],
  ["PAGH_Packets_from_bf6"],
  ["BR_Packets_from_3c1"],
  ["BRIN_Packets_from_3c1"],
  ["SSOL_Packets_from_1e5"],
  ["SSOLIN_Packets_from_1e5"],
  ["BGIN_Packets_from_400", "BGIN_Packets_from_64c"],
  ["BGIN_SC_Packets_from_400", "BGIN_SC_Packets_from_64c"]
]

# Hold event information [supplier_id, event_id, feed_event_id, json_fornatter_int, [Dates]]
events = []

# Event counter will increment after "Add Event"
event_counter = 0

# Hold dates for event being added in
dates = {}

# After adding a date field, this counter will rise by one.
date_counter = 0

# Hold the date labels uses for current event 
date_labels = {}

# Positioning the Date Labels inside the date_canvas and date_frame
date_labels_y_pos = 0

starting_directories = [] # To store first directories found
temp_directories = [] # Will add new subfolders for each directory
supplier_directories = [] # This will hold the final directoires for that supplier
folder_depth = 0 # Will be incremented by one after every folder check

# Verifys that the user has been able to SSH into the jumpbox before
def login_to_server():
  global hostname_str
  global username_str
  global password_str
  hostname = hostname_input.get()
  username = username_input.get()
  password = password_input.get()
  hostname_str = hostname
  username_str = username
  password_str = password
  hostname_input.delete(0, "end")
  username_input.delete(0, "end")
  password_input.delete(0, "end")
  hostname_input["state"] = "disabled"
  hostname_input.delete(0, "end")
  username_input["state"] = "disabled"
  username_input.delete(0, "end")
  password_input["state"] = "disabled"
  password_input.delete(0, "end")
  login_button["state"] = "disabled"
  ssh_client=paramiko.SSHClient()
  ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  try:
    authentication = ssh_client.connect(hostname=hostname_str, username=username_str, password=password_str)
    if authentication is None:
      console_output_field["state"] = "normal"
      console_output_field.insert('end', 'Login has been Successful\n')
      console_output_field["state"] = "disabled"
      username_input["state"] = "disabled"
      username_input.delete(0, "end")
      password_input["state"] = "disabled"
      password_input.delete(0, "end")
      login_button["state"] = "disabled"
      options["state"] = "normal"
      event_id_input["state"] = "normal"
      feed_event_id_input["state"] = "normal"
      add_date_button["state"] = "normal"
      add_event_details["state"] = "normal"
      format_json_button["state"] = "normal"

  except paramiko.AuthenticationException:
    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Login has been Unsuccessful\n')
    console_output_field["state"] = "disabled"
    hostname_input["state"] = "normal"
    hostname_input.delete(0, "end")
    username_input["state"] = "normal"
    username_input.delete(0, "end")
    password_input["state"] = "normal"
    password_input.delete(0, "end")
    login_button["state"] = "normal"
    hostname_str = None
    username_str = None
    password_str = None
    
  except paramiko.ssh_exception.NoValidConnectionsError:
    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Login has been Unsuccessful\n')
    console_output_field["state"] = "disabled"
    hostname_input["state"] = "normal"
    hostname_input.delete(0, "end")
    username_input["state"] = "normal"
    username_input.delete(0, "end")
    password_input["state"] = "normal"
    password_input.delete(0, "end")
    login_button["state"] = "normal"
    hostname_str = None
    username_str = None
    password_str = None

# This functon will act when the supplier has been changed or an event has been added.
# The checkbox will be deselected and the IntVar will be reset to 0
def json_format_unselector():
  global format_json_int
  format_json_int_value = format_json_int.get()
  if format_json_int_value == 1:
    format_json_int.set(0)
    format_json_button.deselect()
  else:
    print("Button Already Deselected")

# Tis will disabled the date based on suppier but will also disabled the JSON formatter for BG events
def date_disabler(value):
  # Disables dates being inputted by the user for LSports and Sportradar events.
  if chosen_options_value.get() == str(supplier_options[0].split(' - ', 1)[1]) or chosen_options_value.get() == str(supplier_options[1].split(' - ', 1)[1]):
    add_date_button["state"] = "disabled"
    delete_date_button["state"] = "disabled"
    for i in range(date_counter):
      delete_date_function()
  else:
    add_date_button["state"] = "normal"
    for i in range(date_counter):
      delete_date_function()
  # Disables the JSON Format Button if the supplier chosen is Betgenius or Betgenius_SC
  if chosen_options_value.get() == str(supplier_options[13].split(' - ', 1)[1]) or chosen_options_value.get() == str(supplier_options[14].split(' - ', 1)[1]):
    format_json_button["state"] = "disabled"
    print("Working")
  else:
    format_json_button["state"] = "normal"

# This function will allow The Labels and DateEntrys to be added with their own keys. Ex - date_label1 or date_12 etc.
def add_date_function():
  global date_counter
  global date_labels_y_pos
  date_labels["date_label{0}".format(date_counter)] = Label(date_frame, text="Date #" + str(date_counter + 1))
  date_labels["date_label{0}".format(date_counter)].grid(column=0, row=date_labels_y_pos, sticky=W, padx=(120,10), pady=5)
  dates["date_{0}".format(date_counter)] = DateEntry(date_frame, values=date_counter, year=2021, state="readonly", date_pattern="yyyy-mm-dd")
  dates["date_{0}".format(date_counter)].grid(column=1, row=date_labels_y_pos, sticky=E, pady=5)
  date_labels_y_pos = date_labels_y_pos + 1
  date_counter = date_counter + 1
  console_output_field["state"] = "normal"
  console_output_field.insert('end', 'Adding Date Field ' + str(date_counter) + ' \n')
  console_output_field["state"] = "disabled"
  console_output_field.see("end")
  # Everytime a date is added into the frame the scrollable bar will become active
  date_canvas.update_idletasks()
  date_canvas.configure(scrollregion=date_canvas.bbox('all'), yscrollcommand=date_canvas_scroll_y.set)
  date_canvas.yview_moveto(1)
  if delete_date_button["state"] == "disabled":
    delete_date_button["state"] = "normal"

# This function will delete the newest date added. If the date_counter is none the button will be disabled
def delete_date_function():
  global date_counter
  global date_labels_y_pos
  date_label_str="date_label{0}".format(date_counter - 1)
  dates_str="date_{0}".format(date_counter - 1)
  date_labels["date_label{0}".format(date_counter - 1)].destroy()
  dates["date_{0}".format(date_counter - 1)].destroy()
  del date_labels[date_label_str]
  del dates[dates_str]
  console_output_field["state"] = "normal"
  console_output_field.insert('end', 'Removing Date Field ' + str(date_counter) + ' \n')
  console_output_field["state"] = "disabled"
  console_output_field.see("end")
  date_labels_y_pos = date_labels_y_pos - 1
  date_counter = date_counter - 1
  # Everytime a date is remeoved from the frame the scrollable bar will update if dates exceed the current view
  date_canvas.update_idletasks()
  date_canvas.configure(scrollregion=date_canvas.bbox('all'), yscrollcommand=date_canvas_scroll_y.set)
  if delete_date_button["state"] == "normal" and date_counter == 0:
    delete_date_button["state"] = "disabled"

# This functions checks all information for the event and validates it before being entered into the array
def add_event_details_function():
  global event_counter
  global date_counter
  global chosen_options_value

  supplier = chosen_options_value.get()
  # checks the supplier options and makes sure that our supplier field will have the same index value as our supplier_options would have
  for i in supplier_options:
    if supplier in i:
      supplier = str(supplier_options.index(i))
      print(supplier)
      if len(supplier) == len(i):
        supplier = str(supplier_options.index(i))
        print(supplier)
      else:
        continue
  # Grab values for event_id, feed_event_id and our json IntVar value
  eventid = event_id_input.get()
  feedeventid = feed_event_id_input.get()
  formatjson = format_json_int.get()

  # If the event_id, feed_event_id or no dates have been entered. The program will prompt you of this
  if not eventid:
    print("Event ID has been left blank")
    console_output_field["state"] = "normal"
    console_output_field.insert('end', "Event ID field cannot be empty" + ' \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    return
  if not feedeventid:
    print("Feed Event ID has been left blank")
    console_output_field["state"] = "normal"
    console_output_field.insert('end', "Feed Event ID field cannot be empty" + ' \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    return
  if not dates and int(supplier) in range(2, 14):
    print("No dates have not been entered")
    console_output_field["state"] = "normal"
    console_output_field.insert('end', "No dates have been selected. Please add in a date" +  ' \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    return
  else:
    print("All inputs are valid")
  
  #Inserts the information into the array
  events.insert(event_counter, [])
  events[event_counter].append(supplier)
  events[event_counter].append(eventid)
  events[event_counter].append(feedeventid)
  events[event_counter].append(formatjson)

  # This checks if the supplier is LSports or Sportsradar. To make sure the function dosnt error a date of 00-00-0000 will be added but is never used.
  if int(events[event_counter][0]) == int(supplier) and not dates: 
    events[event_counter].append('00000000')

  # The next sectionsChecks if all the dates are in the available range on the jumpbox based on the supplier. 
  # If the date isnt in the range the program will prompt us and stop the function
  dates_string = ""
  # Grabs yesterdays date and converts it to an int so we can check all dates for the event.
  yesterday = int(datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d'))

  # This for loop will check every date enetered and check which supplier the event has.
  # Based on this informaiton the loop will check every date to make sure each date can be searched in the jumpbox.
  for idx, val in enumerate(dates):
    if int(events[event_counter][0]) == 2 or 6 or 7 or 8 or range(11,14):
      date = str(dates[val].get_date()).translate({ord('-'):None})
      if int(date) >= 20200429 and int(date) <= yesterday:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(dates[val].get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(dates[val].get_date()) + " "
      else:
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Date " + date + " is not in in range for " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + ' \n')
        console_output_field.insert('end', "Dates must be between dates 2020-04-29 and " + str(datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')) + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Please re-add the event" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        print(event_counter)
        return
    elif int(events[event_counter][0]) == 3:
      date = str(dates[val].get_date()).translate({ord('-'):None})
      if int(date) >= 20200902 and int(date) <= 20210131:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(dates[val].get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(dates[val].get_date()) + " "
      else:
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Date " + date + " is not in in range for " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + ' \n')
        console_output_field.insert('end', "Dates must be between dates 2020-09-02 and 2021-01-31" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Please re-add the event" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        return
    elif int(events[event_counter][0]) == 3 or 4:
      date = str(dates[val].get_date()).translate({ord('-'):None})
      if int(date) >= 20201208 and int(date) <= 20210131:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(dates[val].get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(dates[val].get_date()) + " "
      else:
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Date " + date + " is not in in range for " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + ' \n')
        console_output_field.insert('end', "Dates must be between dates 2020-12-08 and 2021-01-31" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Please re-add the event" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        return
    
    elif int(events[event_counter][0]) == 9:
      date = str(dates[val].get_date()).translate({ord('-'):None})
      if int(date) >= 20200817 and int(date) <= 20201031:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(dates[val].get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(dates[val].get_date()) + " "
      else:
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Date " + date + " is not in in range for " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + ' \n')
        console_output_field.insert('end', "Dates must be between dates 2020-08-17 and 2020-10-31" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Please re-add the event" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        return
    
    elif int(events[event_counter][0]) == 10:
      date = str(dates[val].get_date()).translate({ord('-'):None})
      if int(date) >= 20200817 and int(date) <= 20201130:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(dates[val].get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(dates[val].get_date()) + " "
      else:
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Date " + date + " is not in in range for " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + ' \n')
        console_output_field.insert('end', "Dates must be between dates 2020-08-17 and 2020-11-30" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        console_output_field["state"] = "normal"
        console_output_field.insert('end', "Please re-add the event" + ' \n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        return
  dates_string = dates_string + "\n"

  # Verify's that the event has passed all checks and will be added to the events array
  console_output_field["state"] = "normal"
  if int(events[event_counter][0]) == int(supplier) and not dates:
    console_output_field.insert('end', 'Event ' + str(eventid) + ' with the feed event ' + str(feedeventid) + ' has been added \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
  else:
    console_output_field.insert('end', 'Event ' + str(eventid) + ' with the feed event ' + str(feedeventid) + ' has been added with the following dates:\n')
    console_output_field.insert('end', dates_string)
    console_output_field["state"] = "disabled"
    console_output_field.see("end")

  #Increment the event counter by 1
  event_counter = event_counter + 1

  #Resets everything after adding event details
  chosen_options_value.set(chosen_options_value.get())
  event_id_input.delete(0, "end")
  feed_event_id_input.delete(0, "end")
  for i in range(date_counter):
    delete_date_function()
  start_gathering_packets_details["state"] = "normal"
  json_format_unselector()

# This functions handles everthing regarding files.
# It functons as 
# 1. Finding the folders needed for the supplier
# 2. By using the dates given, it will search the folders for the particular date we need.
# 3. It will then download the zipped file onto the location where the program executes in special folders created based on the supplier 
# (see the supplier_local_folders array)
# 4. The program will start to search for the zipped file for the feed_event_id in each file, WITHOUT having to unzip the file.
# Any file that is found will be stored in an array. After searching all the files in the zip, the program will just extract the files mentioned in the array.
# 5. After these files have been extracted into our Packets_for_Event_xxxxxx folder, it will try to format the JSON files if the option is selected
# OR it will rename some Betgenius files based on the StartTimeUtc on the file.
def start_gathering_packets_details_functions():
  options["state"] = "disabled"
  event_id_input["state"] = "disabled"
  feed_event_id_input["state"] = "disabled"
  add_date_button["state"] = "disabled"
  delete_date_button["state"] = "disabled"
  add_event_details["state"] = "disabled"
  start_gathering_packets_details["state"] = "disabled"
  format_json_button["state"] = "disabled"
  number_of_events = range(len(events))
  events_length_compare = len(events)

  for i in number_of_events:
    number_of_dates = range(4, len(events[i]))
    event_folder = os.path.abspath(os.path.dirname(__file__)) + "/Packets_for_Event_" + str(events[i][1])
    zipped_event_folder = os.path.abspath(os.path.dirname(__file__)) + "/Packets_for_Event_" + str(events[i][1]) + ".zip"
    # The next if else statements will check if the event folder or zip folder already exists
    # If it does exist, the folders and zip will be deleted.
    if os.path.isdir(event_folder):
      if os.path.isfile(zipped_event_folder):
        os.remove(zipped_event_folder)
      shutil.rmtree(event_folder)
      os.makedirs(event_folder)
    else:
      os.makedirs(event_folder)

    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Gathering Packets for Event ' + str(events[i][1]) + '\n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    supplier_directories.clear()
    # Grabs the current time
    start = time.time()

    # Breaks down each date for the event and converts them into year, month and day since the folder structures are in the same format.
    for j in number_of_dates:
      year = events[i][j][0:4]
      month = events[i][j][4:6]
      day = events[i][j][6:8]

      # Grabs the supplier value and is refenced by the val variable
      for idx, val in enumerate(supplier_options):
        if int(events[i][0]) == idx:
          val = val.split(' - ')[0]
          console_output_field["state"] = "normal"
          console_output_field.insert('end', 'Searching for folders this will take some time.\n')
          console_output_field["state"] = "disabled"

          # This function will start to get the directories needed for this supplier.
          def get_directory():
            global folder_depth
            global starting_directories
            chosen_supplier = val
            ssh_client=paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname_str, username=username_str, password=password_str)
            ftp_client=ssh_client.open_sftp()

            # Checking if the Supplier is LSports or Sportsradar and finding the folders for these suppliers
            if chosen_supplier == supplier_options[0].split(' - ')[0] or chosen_supplier == supplier_options[1].split(' - ')[0]:
              print("Supplier is " + chosen_supplier)
              # Our first array of starting_directories will be blank when we begin.
              # This statement will search the root of the server and store the folder names into the arrary with the format
              # /[folder_name]/ ----> /mnt/ or /var/
              if not starting_directories:
                for entry in ftp_client.listdir_attr('/'):
                  mode = entry.st_mode
                  if S_ISDIR(mode):
                    starting_directories.append('/' + entry.filename + '/') 
              # Here we are checking the feed_event_id for the supplier chosen.
              # Since LSports and Sportradars feed event IDs are different in the DB to what is referenced in the folder
              # This code will change the feed event id inputted so that it can find the right folder
              if chosen_supplier == supplier_options[0].split(' - ')[0]:
                if len(events[i][2]) > 7:
                  feed_event_id = events[i][2][:7] # Feed event ID for LSports
                else:
                  feed_event_id = events[i][2] # Feed event ID for LSports
              else:
                feed_event_id = events[i][2][-8:] # Feed event ID for Sportsradar
              
              # Now that the starting directories have the folders in the root of the jumpbox
              # This functon will go into the next set of sub folders and add to the current values
              # Ex ---> /var/ could become /var/html/ or /var/testing/ --- both of these folders will be stored in a temporary folder called
              # temp_directories, the starting directoires will be cleared, and the values in temp_directoires will be added into starting_directoires
              for z in starting_directories:
                try:
                  for entry in ftp_client.listdir_attr(str(z)):
                    mode = entry.st_mode
                    if S_ISDIR(mode):
                      directory = str(z) + entry.filename + '/'
                      if chosen_supplier in directory:
                        # This if statement will check if the supplier is Sportsradar and if it is, the folder will be found and the function will be stopped.
                        if str(feed_event_id) in str(entry.filename) and str(chosen_supplier) == str(supplier_options[1].split(' - ')[0]):
                          print("Found " + chosen_supplier + " Event")
                          print(directory)
                          supplier_directories.append(str(z) + entry.filename + '/')
                          return
                        # This if statement will check if the supplier is LSports and the feed event id is in the directory. 
                        # If the supplier is LSports it will add the folder into the suppliers directory array which is what we want.
                        elif feed_event_id in directory and str(chosen_supplier) == str(supplier_options[0].split(' - ')[0]):
                            print(directory)
                            supplier_directories.append(str(z) + entry.filename + '/')
                        # This else statement is designed for LSports. This will make sure that the folders such as markets_meta will be added into the supplier array.
                        # These folders like markets_meta are important for LSports so we will have
                        # 1 x folder with feed_event_id
                        # 4 x folders such as markets_meta
                        else:
                          if str(chosen_supplier) == str(supplier_options[0].split(' - ')[0]):
                            if not entry.filename.isdigit():
                              supplier_directories.append(str(z) + entry.filename + '/')
                          temp_directories.append(str(z) + entry.filename + '/')
                      else:
                          temp_directories.append(str(z) + entry.filename + '/')
                except WindowsError:
                    continue
              
              # This will check if the desired folders are found
              # If no folders have been found, the temp_directoires values will be merged into the now empty starting_directories.
              # This will allow the get_directory funtion to run again with the new folders added in.
              if not supplier_directories:
                starting_directories.clear()
                starting_directories = starting_directories + temp_directories
                temp_directories.clear()
                get_directory()
              # If we have found the desired folders we will do one more check to make sure the folders are correct when pulling our files
              elif supplier_directories:
                feed_event_ticker = 0
                slash_fix_array = []
                for x in supplier_directories:
                  if feed_event_id in x:
                    print("Found the Feed Event ID")
                    feed_event_ticker = feed_event_ticker + 1
                    starting_directories.clear()
                    temp_directories.clear()
                    slash_fix_array.append(x)
                  # Every directory for every supplier will have more than 4 /'s so this will add the array value into the slash_fix_array.
                  elif str(x).count('/') <= 4:
                    continue
                  else:
                    slash_fix_array.append(x)

                # Adds our fixed value(s) from slash_fix_array into supplier_directories
                supplier_directories.clear()
                supplier_directories.extend(slash_fix_array)
                slash_fix_array.clear()

                # If we never found the feed event ID in our supplier_directories arrays, this if statement will continue our loop of running get_directory
                if feed_event_ticker == 0:
                  starting_directories.clear()
                  starting_directories = starting_directories + temp_directories
                  temp_directories.clear()
                  get_directory()

            # If supplier is anything outside of LSports and Sportsradar
            else:
              # Our first array of starting_directories will be blank when we begin.
              # This statement will search the root of the server and store the folder names into the arrary with the format
              # /[folder_name]/ ----> /mnt/ or /var/
              if not starting_directories:
                for entry in ftp_client.listdir_attr('/'):
                    mode = entry.st_mode
                    if S_ISDIR(mode):
                      starting_directories.append('/' + entry.filename + '/')
                folder_depth = folder_depth + 1
              else:
                folder_depth = folder_depth + 1

              # Now that the starting directories have the folders in the root of the jumpbox
              # This functon will go into the next set of sub folders and add to the current values
              # Ex ---> /var/ could become /var/html/ or /var/testing/ --- both of these folders will be stored in a temporary folder called
              # temp_directories, the starting directoires will be cleared, and the values in temp_directoires will be added into starting_directoires
              for z in starting_directories:
                try:
                  for entry in ftp_client.listdir_attr(str(z)):
                    mode = entry.st_mode
                    if S_ISDIR(mode):
                      directory = str(z) + entry.filename + '/'
                      if chosen_supplier + '/' in directory:
                        if folder_depth >= 4:
                            supplier_directories.append(str(z) + entry.filename + '/')
                      else:
                        if supplier_options[0].split(' - ')[0] in directory:
                            continue
                        elif supplier_options[1].split(' - ')[0] in directory:
                            continue
                        else:
                            temp_directories.append(str(z) + entry.filename + '/')              
                except WindowsError:
                    continue
            
            # This will check if the desired folders are found
            # If no folders have been found, the temp_directoires values will be merged into the now empty starting_directories.
            # This will allow the get_directory funtion to run again with the new folders added in.
            if not supplier_directories:
              starting_directories.clear()
              starting_directories = starting_directories + temp_directories
              temp_directories.clear()
              get_directory()
            else:
              starting_directories.clear()
              temp_directories.clear()
              folder_depth = 0
          
          get_directory()

          console_output_field["state"] = "normal"
          console_output_field.insert('end', 'Folders have been found.\n')
          console_output_field["state"] = "disabled"
          
          # With the folders found for the supplier, this for loop will work on creating the folders to find the remote file(s) needed.
          for folder_num, folder in enumerate(supplier_directories):
            print("Checking directories")
            # If the supplier is LSports or Sportsradar this if statement will run. This if statement will assign the remote and local folders with the values needed.
            if int(0) <= int(idx) <= int(1):
              print("Supplier is " + supplier_options[idx])
              remote_file = f"{folder}"
              digit_folder = None
              if len([int(s) for s in re.findall(r'\b\d+\b', f"{folder}")]) == 0:
                remote_file = f"{folder}"
              else:
                digit_folder = f"{folder}"
              local_file = event_folder + "/Packets"
            # If the supplier is not LSports or Sportsradar this if statement will run. This if statement will assign the remote and local folders with the values needed.
            elif int(2) <= int(idx) <= int(14):
              print("Supplier is " + supplier_options[idx])
              remote_file = f"{folder}{year}/{month}/{day}.tgz"
              folder_dir = os.path.abspath(os.path.dirname(__file__)) + '/' + supplier_local_folders[idx][folder_num] + f'/{year}/{month}/'
              local_file = os.path.abspath(os.path.dirname(__file__)) + '/' + supplier_local_folders[idx][folder_num] + f'/{year}/{month}/{day}.tgz'

            # Checks the suppliers index. If the index is LSports or Sportsradar not additional folders need to be created ourside Packets_for_Event_xxxxx
            # If the supplier isnt either of these, it will created the folder directory that will be referenced for extracting the files.
            if int(0) <= int(idx) <= int(1):
              print(supplier_options[idx].split(' - ', 1)[1] + " didnt need folder")
            elif os.path.exists(folder_dir):
              print("Folder Created")
              print(folder_dir)
            else:
              os.makedirs(folder_dir)
              print(folder_dir)

            # We are now going to be downloading the files needed based on the supplier.
            if os.path.exists(local_file):
              print("File Already Downloaded")
            else:
              console_output_field["state"] = "normal"
              console_output_field.insert('end', 'Found Packets in remote server\n')
              console_output_field["state"] = "disabled"
              console_output_field.see("end")
              # If the supplier is LSports
              if int(idx) == int(0):
                # Opens up the paramiko client so that we can start pulling files from the server
                ssh_client=paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=hostname_str, username=username_str, password=password_str)
                ftp_client=ssh_client.open_sftp()
                print("DOWNLOADING " + remote_file)
                console_output_field["state"] = "normal"
                console_output_field.insert('end', 'Pulling files from ' + remote_file + ' for event ' + str(events[i][1]) + '\n')
                console_output_field["state"] = "disabled"
                console_output_field.see("end")
                # Ths for loop will check every file one by one in the events directory folder
                # It will check for the feed event ID in every file and if this is found the file will be downloaded.
                for filename in ftp_client.listdir(remote_file):
                  ftp_client.get(os.path.join(remote_file, filename), os.path.join(event_folder, filename))
                  opened_file = open(os.path.join(event_folder, filename), "r")
                  read_opened_file = opened_file.read()
                  # If the event is a normal events
                  if len(events[i][2]) == 7:
                    pattern = re.search(str('"FixtureId":' + " " + events[i][2]), str(read_opened_file))
                    pattern_str = str('"FixtureId":' + " " + events[i][2])
                  # If the event is an outright event, it will only search for the first 7 digits
                  # As the first 7 digits are the only ones that would appear in the files.
                  else:
                    pattern = re.search(str('"FixtureId":' + " " + events[i][2][0:7]), str(read_opened_file))
                    pattern_str = str('"FixtureId":' + " " + events[i][2][0:7])

                  # If the pattern (feed_event_id) is found, the file will be closed and a 1_ will be added to the file.
                  # This does not affect anything inside the file, or when replaying the event.
                  # This if else statement is only used for folders in LSports such as markets_meta as not all of the files areneeded for replayability.
                  if pattern != None:
                    print("File " + filename + " has pattern " + pattern_str)
                    console_output_field["state"] = "normal"
                    console_output_field.insert('end', 'File ' + filename + ' has pattern \n')
                    console_output_field.insert('end', 'Renaming ' + filename + ' to filename 1_' + filename + '\n')
                    console_output_field["state"] = "disabled"
                    console_output_field.see("end")
                    read_opened_file = opened_file.close()
                    os.rename(os.path.join(event_folder, filename), os.path.join(event_folder, "1_" + filename))
                  # If the pattern is not found, it will remove the file from the event folder.
                  else:
                    read_opened_file = opened_file.close()
                    os.remove(os.path.join(event_folder, filename))

                if len([int(s) for s in re.findall(r'\b\d+\b', f"{folder}")]) == 0:
                  continue
                else:
                  digit_folder = f"{folder}"

                for filename in ftp_client.listdir(digit_folder):
                  if os.path.exists(os.path.join(event_folder, filename)):
                    continue
                  else:
                    print(filename)
                    ftp_client.get(os.path.join(remote_file, filename), os.path.join(event_folder, filename))
              
              # If the supplier is Sportsradar
              elif int(idx) == int(1):
                ssh_client=paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=hostname_str, username=username_str, password=password_str)
                ftp_client=ssh_client.open_sftp()
                print("DOWNLOADING " + remote_file)
                console_output_field["state"] = "normal"
                console_output_field.insert('end', 'Pulling files from ' + remote_file + ' for event ' + str(events[i][1]) + '\n')
                console_output_field["state"] = "disabled"
                console_output_field.see("end")
                try:
                  for filename in ftp_client.listdir(remote_file):
                    print(filename)
                    ftp_client.get(os.path.join(remote_file, filename), os.path.join(event_folder, filename))
                except IOError:
                  print("Remote Folder not in this directory")
              # If the supplier is not LSports or Sportradar
              else:
                ssh_client=paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=hostname_str, username=username_str, password=password_str)
                console_output_field["state"] = "normal"
                console_output_field.insert('end', 'Pulling files from ' + remote_file + ' for event ' + str(events[i][1]) + '\n')
                console_output_field["state"] = "disabled"
                console_output_field.see("end")
                ftp_client=ssh_client.open_sftp()
                ftp_client.get(remote_file, local_file)
                ftp_client.close()

            console_output_field["state"] = "normal"
            console_output_field.insert('end', 'Packets have been pulled for Event ' + str(events[i][1]) + '\n')
            console_output_field["state"] = "disabled"
            console_output_field.see("end")

            #This if statement is for extracting files from a zip
            # It is not needed for LSports or Sportsradar.
            if int(0) <= int(idx) <= int(1):
              continue
            else:
              console_output_field["state"] = "normal"
              console_output_field.insert('end', 'Extracting packets from Zip ' + str(day) + '.tgz' + '\n')
              console_output_field["state"] = "disabled"
              console_output_field.see("end")
              # Opens the zipped file.
              tar = tarfile.open(local_file, "r:gz")
              # This list will be used to store any files that have been found with the pattern needed.
              files = []
              for member in tar.getmembers():
                f = tar.extractfile(member)
                if f is not None:
                  content = f.read()
                  # If the supplier is PAGH, special rules have to be put in place to find the raceNumber based on the value of the last two digits of the feed_event_id
                  if int(idx) == 8:
                    if int(events[i][2][6:8]) >= 10:
                      print("Found " + str("raceNumber=" + '"' + events[i][2][6:8] + '"'))
                      pattern = re.search(str("raceNumber=" + '"' + events[i][2][6:8] + '"'), str(content))
                      pattern_str = str("raceNumber=" + '"' + events[i][2][6:8] + '"')
                    else:
                      print("Found " + str("raceNumber=" + '"' + events[i][2][7:8] + '"'))
                      pattern = re.search(str("raceNumber=" + '"' + events[i][2][7:8] + '"'), str(content))
                      pattern_str = str("raceNumber=" + '"' + events[i][2][7:8] + '"')
                  else:
                    pattern = re.search(str(events[i][2]), str(content))
                  
                  if pattern != None:
                    if int(idx) == 8:
                      meeting_pattern = re.search(str("meetingId=" + '"' + events[i][2][0:6] + '"'), str(content))
                      if meeting_pattern != None:
                        console_output_field["state"] = "normal"
                        console_output_field.insert('end', "Found " + str("meetingId=" + '"' + events[i][2][0:6] + '"') + '\n')
                        console_output_field["state"] = "disabled"
                        console_output_field.see("end")
                        print("Found " + pattern_str)
                        files.append(member)
                        print(member)
                    else:
                      files.append(member)
                      print(member)
              # If is the method that will tell us which files to extract and where to place them.
              tar.extractall(path = event_folder, members=files)
              tar.close()

              console_output_field["state"] = "normal"
              console_output_field.insert('end', 'Removing folders gathered from remote server \n')
              console_output_field["state"] = "disabled"
              console_output_field.see("end")

              # An extra folder is created inside the events folder which stores out extract files from the zip.
              # This if statement will move all of these files into the root of the Packets_for_Events_xxxxxx folder.
              # If not files were extracted this statement will remove the zipped file to save space.
              if os.path.exists(event_folder + "/" + str(day)):
                files_list = os.listdir(event_folder + "/" + str(day))
                print(event_folder)
                for files in files_list:
                  print(files)
                  shutil.move(os.path.join(event_folder + "/" + str(day), files), os.path.join(event_folder, files))
                os.rmdir(str(event_folder + "/" + str(day)))
                os.remove(local_file)
                shutil.rmtree(os.path.abspath(os.path.dirname(__file__)) + '/' + supplier_local_folders[idx][folder_num] + '/')
              else:
                print("No Files in Folder Exists")
                os.remove(local_file)
                shutil.rmtree(os.path.abspath(os.path.dirname(__file__)) + '/' + supplier_local_folders[idx][folder_num] + '/')
    
    # If the supplier is Betgenius or Betgenius_SC. We can find which files need to be replayed first based on the pattern StartTimeUtc
    # it wll check each file in the Packets_for_Events_xxxxxx folder for this pattern.
    # If the pattern is found, the file is closed and its name will be given an extension of 1_
    # Otherwise the file is left as it was.
    if int(13) <= int(events[i][0]) <= int(14):
      print("Looking for packets with StartTimeUtc")
      event_packets = os.listdir(event_folder)
      for packet in event_packets:
        opened_file = open(os.path.join(event_folder + "/" + packet), "r")
        read_opened_file = opened_file.read()
        pattern = re.search("StartTimeUtc", str(read_opened_file))
        pattern_str = str(events[i][2])
        console_output_field["state"] = "normal"
        console_output_field.insert('end', 'Searching for pattern ' + pattern_str + ' in file ' + packet + '\n')
        console_output_field["state"] = "disabled"
        console_output_field.see("end")
        if pattern != None:
          console_output_field["state"] = "normal"
          console_output_field.insert('end', 'Pattern ' + pattern_str + ' has been found \n')
          console_output_field["state"] = "disabled"
          console_output_field.see("end")
          print(packet)
          read_opened_file = opened_file.close()
          os.rename(os.path.join(event_folder + "/" + packet), os.path.join(event_folder + "/1_" + packet))
    else:
      print("No Files needed to be renamed")

    # This code is our JSON formatter. If the json_format IntVar is equal to 1, it means that the .JSON files in this event should be formatted.
    # This causes issues with replaying BG events so it has ben disabled for now. 
    # While the JSON formats correctly for all events, it has been disabled for this supplier.
    if int(events[i][3]) == 1:
      if int(13) <= int(events[i][0]) <= int(14):
        print("BG Formatter isnt working so skipping")
      else:
        event_packets = os.listdir(event_folder)
        for packet in event_packets:
          if packet.endswith('.json'):
            print(packet)
            console_output_field["state"] = "normal"
            console_output_field.insert('end', 'Fromatting JSON file ' + packet + ' to be more readable \n')
            console_output_field["state"] = "disabled"
            console_output_field.see("end")
            data = None
            with open(os.path.join(event_folder + "/" + packet), 'r') as file:
              data = file.read().replace('\\', '')
              data2 = data.replace('"{', '{')
              data3 = data2.replace('}"', '}')
              try:
                parsed = json.loads(data3)
                parsed_dump = json.dumps(parsed, indent=4)
                with open(os.path.join(event_folder + "/" + packet), "r+") as file:
                  file.truncate(0)
                  file.write(parsed_dump)
                  file.close()
              except json.decoder.JSONDecodeError as err:
                print(f"Invalid JSON: {err}")
                parsed = None
                parsed_dump = None
                parsed = json.loads(data)
                parsed_dump = json.dumps(parsed, indent=4)
                with open(os.path.join(event_folder + "/" + packet), "r+") as file:
                  file.truncate(0)
                  file.write(parsed_dump)
                  file.close()
                continue
    else:
      print("JSON will not be formatted")

    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Zipped Event folder ' + str(events[i][1]) + '\n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    
    # This method will make a zip folder of our event_folder to make extra space.
    shutil.make_archive(os.path.join(event_folder), 'zip', os.path.join(event_folder))

    # This peice of code will start a timer as soon as we hit our Start Packet Gathering button.
    # Once the event has been fully gathered, the timer will stop and output on our console, how long it took to run.
    duration = time.time() - start
    converted_seconds_str = str(duration).split('.', 1)[0]
    converted_seconds_int = int(converted_seconds_str)
    hours, converted_seconds_int =  converted_seconds_int // 3600, converted_seconds_int % 3600
    minutes, converted_seconds_int = converted_seconds_int // 60, converted_seconds_int % 60
    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Packets for Event ' + str(events[i][1]) + ' were gathered in ' + str(hours) + ' Hours ' + str(minutes) + ' Minute and ' + str(converted_seconds_int) + ' Seconds \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end") 

    # Make directories entry for next event
    supplier_directories.clear()

    # After last iteration of array - remove all events and details put into array so other events can be grabbed
    if i == int(events_length_compare - 1):
      global event_counter
      print("This is the last Event in the array")
      console_output_field["state"] = "normal"
      console_output_field.insert('end', 'Packets for all events entered have been gathered. You can input new events if needed. Thank You for using 888 Packet Handler\n')
      console_output_field["state"] = "disabled"
      console_output_field.see("end")
      events.clear()
      event_counter = event_counter - event_counter

      options["state"] = "normal"
      event_id_input["state"] = "normal"
      feed_event_id_input["state"] = "normal"
      chosen_options_value.set(supplier_options[2].split(" - ", 1)[1])
      add_date_button["state"] = "normal"
      delete_date_button["state"] = "disabled"
      add_event_details["state"] = "normal"
      start_gathering_packets_details["state"] = "disabled"
      format_json_button["state"] = "normal"

hostname_label = Label(root, text="Hostname")
hostname_label.place(x=30,y=50)
hostname_input = Entry(root, width=50)
hostname_input.place(x=120, y=50)
      
username_label = Label(root, text="Username")
username_label.place(x=30,y=80)
username_input = Entry(root, width=50)
username_input.place(x=120, y=80)

password_label = Label(root, text="Password")
password_label.place(x=30,y=110)
password_input = Entry(root, width=50, show="*")
password_input.place(x=120, y=110)

login_button = Button(root, text="Login", command=login_to_server)
login_button.place(x=230,y=150)

chosen_options_value = StringVar(root)
chosen_options_value.set(supplier_options[2].split(" - ", 1)[1])

options = OptionMenu(root, chosen_options_value, supplier_options[0].split(" - ", 1)[1], supplier_options[1].split(" - ", 1)[1], supplier_options[2].split(" - ", 1)[1], supplier_options[3].split(" - ", 1)[1], supplier_options[4].split(" - ", 1)[1], supplier_options[5].split(" - ", 1)[1], supplier_options[6].split(" - ", 1)[1], supplier_options[7].split(" - ", 1)[1], supplier_options[8].split(" - ", 1)[1], supplier_options[9].split(" - ", 1)[1], supplier_options[10].split(" - ", 1)[1], supplier_options[11].split(" - ", 1)[1], supplier_options[12].split(" - ", 1)[1], supplier_options[13].split(" - ", 1)[1], supplier_options[14].split(" - ", 1)[1], command=date_disabler)
options.place(x=195, y=270)
options["state"] = "disabled"

event_id_label = Label(root, text="Event ID")
event_id_label.place(x=30, y=310)
event_id_input = Entry(root, width=50)
event_id_input["state"] = "disabled"
event_id_input.place(x=120, y=310)

feed_event_id_label = Label(root, text="Feed Event ID")
feed_event_id_label.place(x=30, y=340)
feed_event_id_input = Entry(root, width=50)
feed_event_id_input["state"] = "disabled"
feed_event_id_input.place(x=120,y=340)

format_json_int = IntVar()
format_json_button = Checkbutton(root, text="Format JSON?", variable=format_json_int)
format_json_button.place(x=450, y=325)
format_json_button["state"] = "disabled"

add_date_button = Button(root, text="Add Date Field", command=add_date_function)
add_date_button["state"] = "disabled"
add_date_button.place(x=30,y=370)

delete_date_button = Button(root, text="Delete Date Field", command=delete_date_function)
delete_date_button["state"] = "disabled"
delete_date_button.place(x=140,y=370)

add_event_details = Button(root, text="Add Event", command=add_event_details_function)
add_event_details["state"] = "disabled"
add_event_details.place(x=260,y=370)

#start_gathering_packets_details = Button(root, text="Start Packet Gathering", command=start_gathering_packets_details_functions)
start_gathering_packets_details = Button(root, text="Start Packet Gathering", command=lambda:threading.Thread(target=start_gathering_packets_details_functions).start())
start_gathering_packets_details["state"] = "disabled"
start_gathering_packets_details.place(x=350, y=370)

# Vertical (y) Scroll Bar
yscrollbar = Scrollbar(root)
yscrollbar.pack(side=RIGHT, fill=Y)

console_output_label = Label(root, text="All Logs - Login Success, Events Added, Packet Progress")
console_output_label.place(x=800, y=60)
console_output_field = Text(root, wrap=WORD, yscrollcommand=yscrollbar.set)
console_output_field["state"] = "disabled"
console_output_field.place(x=600, y=80)
console_output_field.config(height = 40)

yscrollbar.place(in_=console_output_field, relx=1.0, relheight=1.0, bordermode="outside")
yscrollbar.config(command=console_output_field.yview)

#Scrollable Date Sections
date_canvas = Canvas(root, width=450, height = 200)
date_canvas_scroll_y = Scrollbar(root, orient="vertical", command=date_canvas.yview)
date_frame = Frame(date_canvas)

# put the frame in the canvas
date_canvas.create_window(0, 0, anchor='nw', window=date_frame)
# make sure everything is displayed before configuring the scrollregion
date_canvas.update_idletasks()
date_canvas.configure(scrollregion=date_canvas.bbox('all'), yscrollcommand=date_canvas_scroll_y.set)            
date_canvas.pack(fill='both', side='left')
date_canvas_scroll_y.pack(fill='y', side='right')
date_canvas_scroll_y.place(in_=date_canvas, relx=1.0, relheight=1.0, bordermode="outside")
date_canvas.place(x=50, y=430)

root.mainloop()
