import os
import re
import shutil
import tarfile
import paramiko
import suppliers
import json

def create_folders(event):
    event_folder = os.path.abspath(os.path.dirname(__file__)) + "/Packets_for_Event_" + event
    if os.path.isdir(event_folder):
      shutil.rmtree(event_folder)
      os.makedirs(event_folder)
    else:
      os.makedirs(event_folder)
    return event_folder

def download_filter_day(supplier, host, feed_event_id, event_folder_zipped, event_folder, supplier_folder, username, password, day, tag):
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    ssh_client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
    ftp_client=ssh_client.open_sftp()
    ftp_client.get(supplier_folder, event_folder_zipped)
    ftp_client.close()

    tar = tarfile.open(event_folder_zipped, "r:gz")
    # This list will be used to store any files that have been found with the pattern needed.
    files = []
    for member in tar.getmembers():
        f = tar.extractfile(member)
        if f is not None:
            content = json.loads(f.read())
            if content[tag] == feed_event_id:
                files.append(member)
            #content = f.read()
            #pattern = re.search('"' + "eventId" + '"' + ':' + '"' + feed_event_id + '"', str(content))
           # if pattern != None:
                #print(member)
                #files.append(member)
    tar.extractall(path = event_folder, members=files)
    tar.close()

    if os.path.exists(f"{event_folder}/{day}"):
        files_list = os.listdir(f"{event_folder}/{day}")
        for files in files_list:
            shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
        shutil.rmtree(f"{event_folder}/{day}")
        os.remove(event_folder_zipped)
    else:
        os.remove(event_folder_zipped)