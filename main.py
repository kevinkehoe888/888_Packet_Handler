from http import server
from tkinter import *
import os
import paramiko

# How to build
# pyinstaller --onefile --hidden-import babel.numbers --windowed 888_Packet_Handler.py

known_host_servers, known_host_optionMenu = [], []
succesful_login = 0

root = Tk()
root.title("888 Packet Handler")
root.geometry("1000x500")

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

def login_to_server(username, password):
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
        login_button["state"] = "disabled"
        print(f"SUCCESSFUL LOGINS {succesful_login}")



username_label = Label(root, text="Username")
username_label.place(x=30,y=30)
username_input = Entry(root, width=30)
username_input.place(x=120, y=30)

password_label = Label(root, text="Password")
password_label.place(x=30,y=60)
password_input = Entry(root, width=30, show="*")
password_input.place(x=120, y=60)

login_button = Button(root, text="Login", command=lambda:login_to_server(username_input.get(), password_input.get()))
login_button.place(x=180,y=90)

root.mainloop()
