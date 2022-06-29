import os
import re
import shutil
import paramiko

def create_folders(event):
    event_folder = os.path.abspath(os.path.dirname(__file__)) + "/Packets_for_Event_" + event
    if os.path.isdir(event_folder):
      shutil.rmtree(event_folder)
      os.makedirs(event_folder)
    else:
      os.makedirs(event_folder)
    return event_folder

def lsport_download_folders(supplier, host, feed_event_id, event_folder, username, password, folder_one_verify, folder_two_verify, chosen_directories):
    #print(supplier, host, feed_event_id, event_folder, username, password, folder_one_verify, folder_two_verify, chosen_directories)
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    ssh_client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
    ftp_client=ssh_client.open_sftp()
    try:
        print("Try first folder structure")
        for filename in ftp_client.listdir(folder_one_verify):
            ftp_client.get(f"{folder_one_verify}/{filename}", os.path.join(event_folder, filename))
    except FileNotFoundError:
        print("First folder structure failed - Trying second structure.")
        try:
            for filename in ftp_client.listdir(folder_two_verify):
                ftp_client.get(f"{folder_two_verify}/{filename}", os.path.join(event_folder, filename))
        except FileNotFoundError:
            print("Folder does not exist - please double check the event")

    if len(feed_event_id) > 7:
        feed_event_id = feed_event_id[0:7]

    for i in chosen_directories:
        for filename in ftp_client.listdir(i):
            print(f"Checking {filename}")
            ftp_client.get(f"{i}/{filename}", os.path.join(event_folder, filename))
            opened_file = open(os.path.join(event_folder, filename), "r")
            read_opened_file = opened_file.read()
            pattern = re.search(str('"FixtureId":' + " " + feed_event_id), str(read_opened_file))
            if pattern != None:
                read_opened_file = opened_file.close()
                os.rename(os.path.join(event_folder, filename), os.path.join(event_folder, "1_" + filename))
            else:
                read_opened_file = opened_file.close()
                os.remove(os.path.join(event_folder, filename))

def sportsradar_download_folders(supplier, host, feed_event_id, event_folder, chosen_directories, username, password):
    feed_event_id_folder = f"sr_match{feed_event_id[-8:]}"
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    ssh_client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
    ftp_client=ssh_client.open_sftp()
    for i in chosen_directories:
        try:
            for filename in ftp_client.listdir(f"{i}/{feed_event_id_folder}"):
                ftp_client.get(f"{i}/{feed_event_id_folder}/{filename}", os.path.join(event_folder, filename))
        except IOError:
            print("Remote Folder not in this directory")