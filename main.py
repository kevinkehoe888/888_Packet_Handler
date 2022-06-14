from tkinter import *
from tkcalendar import DateEntry
import os
import paramiko

# How to build
# pyinstaller --onefile --hidden-import babel.numbers --windowed 888_Packet_Handler.py

known_host_servers, known_host_optionMenu = [], []
date_labels, dates = {}, {}
successful_login, date_counter, date_labels_y_pos = 0, 0, 0

root = Tk()
root.title("888 Packet Handler")
root.geometry("1000x550")

supplier_options = [
  ["lsport", "LSports"],
  ["sportradar", "SportRadar"],
  ["METRIC", "Metric Gaming"],
  ["AT_THE_RACES", "At The Races"],
  ["RACING_UK", "Racing UK"],
  ["SIS", "SPIN Horse Racing"],
  ["CMT", "CMT"],
  ["PA", "Press Association"],
  ["PAGH", "Dogs"],
  ["BR", "BetRadar"],
  ["BRIN", "BetRadar Inplay"],
  ["SSOL", "Sporting Solutions"],
  ["SSOLIN", "Sporting Solutions InPlay"],
  ["BGIN", "BetGenius"],
  ["BGIN_SC", "BetGenius_SC"]
]

def login_to_server(username, password, successful_login):
    username_input.delete(0, "end")
    username_input["state"] = "disabled"
    password_input.delete(0, "end")
    password_input["state"] = "disabled"
    login_button["state"] = "disabled"

    with open(os.path.expanduser('~/.ssh/known_hosts'), 'r') as reader:
        while (line := reader.readline()):
            if line.partition(' ')[0].partition(',')[0][0].isalpha() and "jump." in line:
              if line.partition(' ')[0].partition(',')[0] in known_host_servers:
                print(f"{line.partition(' ')[0].partition(',')[0]} already in known_host_servers array")
              else:
                known_host_servers.append(line.partition(' ')[0].partition(',')[0])
                print(f"Adding {line.partition(' ')[0].partition(',')[0]} to known_host_servers array")
    
    client = paramiko.SSHClient()

    try:
        client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    except:
        print('File could not be read')
    else:
        print('Known host files has been loaded')

    for index, host in enumerate(known_host_servers):
        server = host[13:]
        server = server[:-4].upper()
        try:
            client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
        except paramiko.ssh_exception.BadHostKeyException:
            print('The host key given by the SSH server did not match what we were expecting.')
            username_input["state"] = "normal"
            password_input["state"] = "normal"
            login_button["state"] = "normal"
        except paramiko.ssh_exception.AuthenticationException:
            print('Authentication failed for some reason')
            username_input["state"] = "normal"
            password_input["state"] = "normal"
            login_button["state"] = "normal"
        else:
            print('Connection to server has been successful')
            client.close()
            succesful_login += 1
            known_host_optionMenu.append(server)
            print(known_host_optionMenu[index], known_host_servers[index])

    if succesful_login != 0:
        username_input["state"] = "disabled"
        password_input["state"] = "disabled"
        login_button["state"] = "disabled"
        add_date_button["state"] = "normal"
        delete_date_button["state"] = "disabled"
        add_event_details["state"] = "normal"
        start_gathering_packets_details["state"] = "disabled"
        server_options["state"] = "normal"

        #Loading Supplier Dropdown
        chosen_options_value = StringVar(root)
        chosen_options_value.set(supplier_options[2][1])
        options = OptionMenu(root, chosen_options_value, supplier_options[0][1], supplier_options[1][1], supplier_options[2][1], supplier_options[3][1], supplier_options[4][1], supplier_options[5][1], supplier_options[6][1], supplier_options[7][1], supplier_options[8][1], supplier_options[9][1], supplier_options[10][1], supplier_options[11][1], supplier_options[12][1], supplier_options[13][1], supplier_options[14][1])#, command=date_disabler)
        options.place(x=115, y=270)

        # Loading Server Dropdown
        chosen_server_value = StringVar(root)
        chosen_server_value.set(known_host_optionMenu[0])
        server_options = OptionMenu(root, chosen_server_value, *known_host_optionMenu)
        server_options.place(x=350, y=270)
        print(f"SUCCESSFUL LOGINS {succesful_login}")

# This function will allow The Labels and DateEntrys to be added with their own keys. Ex - date_label1 or date_12 etc.
def add_date_function():
  global date_counter
  global date_labels_y_pos
  date_labels["date_label{0}".format(date_counter)] = Label(date_frame, text="Date #" + str(date_counter + 1))
  date_labels["date_label{0}".format(date_counter)].grid(column=0, row=date_labels_y_pos, sticky=W, padx=(120,10), pady=5)
  dates["date_{0}".format(date_counter)] = DateEntry(date_frame, values=date_counter, year=2022, state="readonly", date_pattern="yyyy-mm-dd")
  dates["date_{0}".format(date_counter)].grid(column=1, row=date_labels_y_pos, sticky=E, pady=5)
  date_labels_y_pos = date_labels_y_pos + 1
  date_counter = date_counter + 1

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
  date_labels_y_pos = date_labels_y_pos - 1
  date_counter = date_counter - 1
  # Everytime a date is remeoved from the frame the scrollable bar will update if dates exceed the current view
  date_canvas.update_idletasks()
  date_canvas.configure(scrollregion=date_canvas.bbox('all'), yscrollcommand=date_canvas_scroll_y.set)
  if delete_date_button["state"] == "normal" and date_counter == 0:
    delete_date_button["state"] = "disabled"

username_label = Label(root, text="Username")
username_label.place(x=30,y=30)
username_input = Entry(root, width=30)
username_input.place(x=120, y=30)

password_label = Label(root, text="Password")
password_label.place(x=30,y=60)
password_input = Entry(root, width=30, show="*")
password_input.place(x=120, y=60)

login_button = Button(root, text="Login", command=lambda:login_to_server(username_input.get(), password_input.get(), successful_login))
login_button.place(x=180,y=90)

supplier_label = Label(root, text="Supplier: ")
supplier_label.place(x=400,y=18)

server_label = Label(root, text="Server: ")
server_label.place(x=670,y=18)

event_id_label = Label(root, text="Event ID")
event_id_label.place(x=400, y=50)
event_id_input = Entry(root, width=50)
event_id_input["state"] = "disabled"
event_id_input.place(x=490, y=50)

feed_event_id_label = Label(root, text="Feed Event ID")
feed_event_id_label.place(x=400, y=80)
feed_event_id_input = Entry(root, width=50)
feed_event_id_input["state"] = "disabled"
feed_event_id_input.place(x=490,y=80)

add_date_button = Button(root, text="Add Date Field", command=add_date_function)
add_date_button["state"] = "disabled"
add_date_button.place(x=400,y=110)

delete_date_button = Button(root, text="Delete Date Field", command=delete_date_function)
delete_date_button["state"] = "disabled"
delete_date_button.place(x=510,y=110)

add_event_details = Button(root, text="Add Event")#, command=add_event_details_function)
add_event_details["state"] = "disabled"
add_event_details.place(x=630,y=110)

start_gathering_packets_details = Button(root, text="Start Packet Gathering")#, command=lambda:threading.Thread(target=start_gathering_packets_details_functions).start())
start_gathering_packets_details["state"] = "disabled"
start_gathering_packets_details.place(x=720, y=110)

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
date_canvas.place(x=420, y=150)

root.mainloop()
