from tkinter import *
from tkinter import filedialog
from tkcalendar import DateEntry
import paramiko
import time
from datetime import datetime, timedelta
import os
import tarfile
import re
import shutil
import threading
import tempfile
import binascii
import atexit
from stat import S_ISDIR, S_ISREG

# How to build
# pyinstaller --onefile --hidden-import babel.numbers --windowed 888_Packet_Handler.py

# When current events have been gathered, remove them from array so you dont have to close and reopen script

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

events = []
event_counter = 0

dates = []
date_counter = 0

date_labels = []
date_labels_y_pos = 420

starting_directories = [] # To store fist directories found
temp_directories = [] # Will add new subfolders for each directory
supplier_directories = [] # This will hold the final directoires for that supplier
folder_depth = 0

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
      delete_date_button["state"] = "normal"
      add_event_details["state"] = "normal"
      start_gathering_packets_details["state"] = "normal"

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

def date_disabler(value):
  if chosen_options_value.get() == str(supplier_options[0].split(' - ', 1)[1]) or chosen_options_value.get() == str(supplier_options[1].split(' - ', 1)[1]):
    add_date_button["state"] = "disabled"
    delete_date_button["state"] = "disabled"
  else:
    add_date_button["state"] = "normal"
    delete_date_button["state"] = "normal"

def add_date_function():
  global date_counter
  global date_labels_y_pos
  date_labels.append(Label(root, text="Date #" + str(date_counter + 1)))
  date_labels[date_counter].place(x=160, y=date_labels_y_pos)
  dates.append(DateEntry(root, values=date_counter, year=2021, state="readonly", date_pattern="yyyy-mm-dd"))
  dates[date_counter].place(x=220,y=date_labels_y_pos)
  date_labels_y_pos = date_labels_y_pos + 30
  date_counter = date_counter + 1
  console_output_field["state"] = "normal"
  console_output_field.insert('end', 'Adding Date Field ' + str(date_counter) + ' \n')
  console_output_field["state"] = "disabled"
  console_output_field.see("end")

def delete_date_function():
  global date_counter
  global date_labels_y_pos
  date_labels[date_counter - 1].destroy()
  dates[date_counter - 1].destroy()
  del date_labels[date_counter - 1]
  del dates[date_counter - 1]
  console_output_field["state"] = "normal"
  console_output_field.insert('end', 'Removing Date Field ' + str(date_counter) + ' \n')
  console_output_field["state"] = "disabled"
  console_output_field.see("end")
  date_labels_y_pos = date_labels_y_pos - 30
  date_counter = date_counter - 1

def add_event_details_function():
  global event_counter
  global date_counter
  global chosen_options_value

  supplier = chosen_options_value.get()
  #Grab values for Supplier, event_id and feed_event_id
  for i in supplier_options:
    if supplier in i:
      supplier = str(supplier_options.index(i))
      print(supplier)
      if len(supplier) == len(i):
        supplier = str(supplier_options.index(i))
        print(supplier)
      else:
        continue
  #supplier = str(supplier_options.index(chosen_options_value.get()))
  eventid = event_id_input.get()
  feedeventid = feed_event_id_input.get()

  #Add code to check all inputs - If any are blank - return error and end the function
  if not eventid:
    print("Event ID has been left blank")
    console_output_field["state"] = "normal"
    console_output_field.insert('end', "Event ID field cannot be empty" + ' \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    return
  elif not feedeventid:
    print("Feed Event ID has been left blank")
    console_output_field["state"] = "normal"
    console_output_field.insert('end', "Feed Event ID field cannot be empty" + ' \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    return
  #elif not dates and int(supplier_options.index(chosen_options_value.get())) == 0 and int(supplier_options.index(chosen_options_value.get())) == 1:
  elif not dates and int(supplier) == 0 and int(supplier) == 1:
    print("LSports or Sportadars Event")
    return
  #elif not dates and int(supplier_options.index(chosen_options_value.get())) in range(2, 14):
  elif not dates and int(supplier) in range(2, 14):
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

  #if int(events[event_counter][0]) == supplier_options.index('LSports') and not dates: 
  if int(events[event_counter][0]) == int(supplier) and not dates: 
    events[event_counter].append('00000000')
  #elif int(events[event_counter][0]) == supplier_options.index('SportRadar') and not dates:
  elif int(events[event_counter][0]) == int(supplier) and not dates:
    events[event_counter].append('00000000')

  #Adds all the event into the array and sets counter up for next one
  dates_string = ""
  yesterday = int(datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d'))
  for i in dates:
    if int(events[event_counter][0]) == 2 or 6 or 7 or 8 or range(11,14):#supplier_options.index('Metric Gaming') or int(events[event_counter][0]) == supplier_options.index('CMT') or int(events[event_counter][0]) == supplier_options.index('PA - Press Association') or int(events[event_counter][0]) == supplier_options.index('PAGH - Dogs') or int(events[event_counter][0]) == supplier_options.index('SSOL - Sporting Solutions') or int(events[event_counter][0]) == supplier_options.index('SSOLIN - Sporting Solutions InPlay') or int(events[event_counter][0]) == supplier_options.index('BGIN - BetGenius') or int(events[event_counter][0]) == supplier_options.index('BGIN_SC - BetGenius_SC'):
      date = str(i.get_date()).translate({ord('-'):None})
      if int(date) >= 20200429 and int(date) <= yesterday:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(i.get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(i.get_date()) + " "
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
    elif int(events[event_counter][0]) == 3: #supplier_options.index('At The Races'):
      date = str(i.get_date()).translate({ord('-'):None})
      if int(date) >= 20200902 and int(date) <= 20210131:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(i.get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(i.get_date()) + " "
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

    elif int(events[event_counter][0]) == 3 or 4: # supplier_options.index('Racing UK') or int(events[event_counter][0]) == supplier_options.index('SIS - SPIN Horse Racing'):
      date = str(i.get_date()).translate({ord('-'):None})
      if int(date) >= 20201208 and int(date) <= 20210131:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(i.get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(i.get_date()) + " "
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
    
    elif int(events[event_counter][0]) == 9:#supplier_options.index('BR - BetRadar'):
      date = str(i.get_date()).translate({ord('-'):None})
      if int(date) >= 20200817 and int(date) <= 20201031:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(i.get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(i.get_date()) + " "
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
    
    elif int(events[event_counter][0]) == 10:#supplier_options.index('BRIN - BetRadar Inplay'):
      date = str(i.get_date()).translate({ord('-'):None})
      if int(date) >= 20200817 and int(date) <= 20201130:
        print("Date for supplier " + str(supplier_options[int(supplier)].split(" - ", 1)[1]) + " is " + date)
        events[event_counter].append(str(i.get_date()).translate({ord('-'):None}))
        dates_string = dates_string + str(i.get_date()) + " "
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
    #events[event_counter].append(str(i.get_date()).translate({ord('-'):None}))
    #dates_string = dates_string + str(i.get_date()) + " "
  dates_string = dates_string + "\n"

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

  event_counter = event_counter + 1

  #Resets everything after adding event details
  #chosen_options_value.set(supplier_options[2])
  chosen_options_value.set(chosen_options_value.get())
  event_id_input.delete(0, "end")
  feed_event_id_input.delete(0, "end")
  for i in range(date_counter):
    delete_date_function()
  #[[supplier_id, event_id, feed_event_id , date1, date2, etc]]

def start_gathering_packets_details_functions():
  options["state"] = "disabled"
  event_id_input["state"] = "disabled"
  feed_event_id_input["state"] = "disabled"
  add_date_button["state"] = "disabled"
  delete_date_button["state"] = "disabled"
  add_event_details["state"] = "disabled"
  start_gathering_packets_details["state"] = "disabled"
  number_of_events = range(len(events))
  events_length_compare = len(events)
  for i in number_of_events:
    number_of_dates = range(3, len(events[i]))
    event_folder = os.path.abspath(os.path.dirname(__file__)) + "/Packets_for_Event_" + str(events[i][1])
    if os.path.isdir(event_folder):
      continue
    else:
      os.makedirs(event_folder)
    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Gathering Packets for Event ' + str(events[i][1]) + '\n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")
    supplier_directories.clear()
    start = time.time()
    for j in number_of_dates:
      year = events[i][j][0:4]
      month = events[i][j][4:6]
      day = events[i][j][6:8]
      for idx, val in enumerate(supplier_options):
        if int(events[i][0]) == idx:
          val = val.split(' - ')[0]
          console_output_field["state"] = "normal"
          console_output_field.insert('end', 'Searching for folders this will take some time.\n')
          console_output_field["state"] = "disabled"
          def get_directory():
            global folder_depth
            global starting_directories
            chosen_supplier = val
            ssh_client=paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname_str, username=username_str, password=password_str)
            ftp_client=ssh_client.open_sftp()

            # Checking if the Supplier is LSports or Sportsradar
            if chosen_supplier == supplier_options[0].split(' - ')[0] or chosen_supplier == supplier_options[1].split(' - ')[0]:
              print("Supplier is " + chosen_supplier)
              if not starting_directories:
                for entry in ftp_client.listdir_attr('/'):
                  mode = entry.st_mode
                  if S_ISDIR(mode):
                    starting_directories.append('/' + entry.filename + '/')     
              if chosen_supplier == supplier_options[0].split(' - ')[0]:
                if len(events[i][2]) == 10:
                  feed_event_id = events[i][2][:7]
                  print(feed_event_id)
                else:
                  feed_event_id = events[i][2]
                #print(feed_event_id)
              else:
                feed_event_id = events[i][2][-8:]
                #print(feed_event_id)
              
              for z in starting_directories:
                try:
                  for entry in ftp_client.listdir_attr(str(z)):
                    mode = entry.st_mode
                    if S_ISDIR(mode):
                      directory = str(z) + entry.filename + '/'
                      if chosen_supplier in directory:
                        if str(feed_event_id) in str(entry.filename) and str(chosen_supplier) == str(supplier_options[1].split(' - ')[0]):
                          print("Found " + chosen_supplier + " Event")
                          print(directory)
                          supplier_directories.append(str(z) + entry.filename + '/')
                          return
                        elif feed_event_id in directory and str(chosen_supplier) == str(supplier_options[0].split(' - ')[0]):
                            print(directory)
                            supplier_directories.append(str(z) + entry.filename + '/')
                        else:
                          if str(chosen_supplier) == str(supplier_options[0].split(' - ')[0]):
                            if not entry.filename.isdigit():
                              supplier_directories.append(str(z) + entry.filename + '/')
                          temp_directories.append(str(z) + entry.filename + '/')
                      else:
                          temp_directories.append(str(z) + entry.filename + '/')
                except WindowsError:
                    continue

              if not supplier_directories:
                starting_directories.clear()
                starting_directories = starting_directories + temp_directories
                temp_directories.clear()
                get_directory()
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
                  elif str(x).count('/') <= 4:
                    continue
                  else:
                    slash_fix_array.append(x)
                
                supplier_directories.clear()
                supplier_directories.extend(slash_fix_array)
                slash_fix_array.clear()

                if feed_event_ticker == 0:
                  starting_directories.clear()
                  starting_directories = starting_directories + temp_directories
                  temp_directories.clear()
                  get_directory()

            else:
              if not starting_directories:
                for entry in ftp_client.listdir_attr('/'):
                    mode = entry.st_mode
                    if S_ISDIR(mode):
                      starting_directories.append('/' + entry.filename + '/')
                folder_depth = folder_depth + 1
              else:
                folder_depth = folder_depth + 1

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
          
          for folder_num, folder in enumerate(supplier_directories):
            print("Checking directories")
            if int(0) <= int(idx) <= int(1):
              print("Supplier is " + supplier_options[idx])
              remote_file = f"{folder}"
              digit_folder = None
              if len([int(s) for s in re.findall(r'\b\d+\b', f"{folder}")]) == 0:
                remote_file = f"{folder}"
              else:
                digit_folder = f"{folder}"
              local_file = event_folder + "/Packets"
            elif int(2) <= int(idx) <= int(14):
              print("Supplier is " + supplier_options[idx])
              remote_file = f"{folder}{year}/{month}/{day}.tgz"
              folder_dir = os.path.abspath(os.path.dirname(__file__)) + '/' + supplier_local_folders[idx][folder_num] + f'/{year}/{month}/'
              local_file = os.path.abspath(os.path.dirname(__file__)) + '/' + supplier_local_folders[idx][folder_num] + f'/{year}/{month}/{day}.tgz'

            if int(0) <= int(idx) <= int(1):
              print(supplier_options[idx].split(' - ', 1)[1] + " didnt need folder")
            elif os.path.exists(folder_dir):
              print("Folder Created")
              print(folder_dir)
            else:
              os.makedirs(folder_dir)
              print(folder_dir)

            if os.path.exists(local_file):
              print("File Already Downloaded")
            else:
              console_output_field["state"] = "normal"
              console_output_field.insert('end', 'Found Packets in remote server\n')
              console_output_field["state"] = "disabled"
              console_output_field.see("end")
              if int(idx) == int(0):
                ssh_client=paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=hostname_str, username=username_str, password=password_str)
                ftp_client=ssh_client.open_sftp()
                print("DOWNLOADING " + remote_file)
                console_output_field["state"] = "normal"
                console_output_field.insert('end', 'Pulling files from ' + remote_file + ' for event ' + str(events[i][1]) + '\n')
                console_output_field["state"] = "disabled"
                console_output_field.see("end")
                for filename in ftp_client.listdir(remote_file):
                  ftp_client.get(os.path.join(remote_file, filename), os.path.join(event_folder, filename))
                  opened_file = open(os.path.join(event_folder, filename), "r")
                  read_opened_file = opened_file.read()
                  if len(events[i][2]) == 7:
                    pattern = re.search(str('"FixtureId":' + " " + events[i][2]), str(read_opened_file))
                    pattern_str = str('"FixtureId":' + " " + events[i][2])
                  else:
                    pattern = re.search(str('"FixtureId":' + " " + events[i][2][0:7]), str(read_opened_file))
                    pattern_str = str('"FixtureId":' + " " + events[i][2][0:7])

                  if pattern != None:
                    print("File " + filename + " has pattern " + pattern_str)
                    console_output_field["state"] = "normal"
                    console_output_field.insert('end', 'File ' + filename + ' has pattern \n')
                    console_output_field.insert('end', 'Renaming ' + filename + ' to filename 1_' + filename + '\n')
                    console_output_field["state"] = "disabled"
                    console_output_field.see("end")
                    read_opened_file = opened_file.close()
                    os.rename(os.path.join(event_folder, filename), os.path.join(event_folder, "1_" + filename))
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

            if int(0) <= int(idx) <= int(1):
              continue
            else:
              console_output_field["state"] = "normal"
              console_output_field.insert('end', 'Extracting packets from Zip ' + str(day) + '.tgz' + '\n')
              console_output_field["state"] = "disabled"
              console_output_field.see("end")
              tar = tarfile.open(local_file, "r:gz")
              files = []
              for member in tar.getmembers():
                f = tar.extractfile(member)
                if f is not None:
                  content = f.read()
                  if int(idx) == 8:
                    if int(events[i][2][6:8]) >= 10:
                      #print("Found " + str("raceNumber=" + '"' + events[i][2][6:8] + '"'))
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
              tar.extractall(path = event_folder, members=files)
              tar.close()

              console_output_field["state"] = "normal"
              console_output_field.insert('end', 'Removing folders gathered from remote server \n')
              console_output_field["state"] = "disabled"
              console_output_field.see("end")

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
    
    #if str(events[i][0]) == "13" or str(events[i][0]) == "14":
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

    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Zipped Event folder ' + str(events[i][1]) + '\n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end")

    shutil.make_archive(os.path.join(event_folder), 'zip', os.path.join(event_folder))
    duration = time.time() - start
    converted_seconds_str = str(duration).split('.', 1)[0]
    converted_seconds_int = int(converted_seconds_str)
    hours, converted_seconds_int =  converted_seconds_int // 3600, converted_seconds_int % 3600
    minutes, converted_seconds_int = converted_seconds_int // 60, converted_seconds_int % 60
    console_output_field["state"] = "normal"
    console_output_field.insert('end', 'Packets for Event ' + str(events[i][1]) + ' were gathered in ' + str(hours) + ' Hours ' + str(minutes) + ' Minute and ' + str(converted_seconds_int) + ' Seconds \n')
    console_output_field["state"] = "disabled"
    console_output_field.see("end") 

    options["state"] = "normal"
    event_id_input["state"] = "normal"
    feed_event_id_input["state"] = "normal"
    add_date_button["state"] = "normal"
    delete_date_button["state"] = "normal"
    add_event_details["state"] = "normal"
    start_gathering_packets_details["state"] = "normal"

    # Make directories entry for next event
    supplier_directories.clear()

    #After last iteration of array - remove all events and details put into array so other events can be grabbed
    if i == int(events_length_compare - 1):
      global event_counter
      print("This is the last Event in the array")
      console_output_field["state"] = "normal"
      console_output_field.insert('end', 'Packets for all events entered have been gathered. You can input new events if needed. Thank You for using 888 Packet Handler\n')
      console_output_field["state"] = "disabled"
      console_output_field.see("end")
      events.clear()
      event_counter = event_counter - event_counter

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

root.mainloop()
