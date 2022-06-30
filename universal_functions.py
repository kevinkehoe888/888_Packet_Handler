import os
import re
import sys
import shutil
import paramiko

def create_folders(event):
    if getattr(sys, 'frozen', False):
        event_folder = os.path.dirname(os.path.realpath(sys.executable)) + "/Packets_for_Event_" + event
    else:
        os.path.abspath(os.path.dirname(__file__)) + "/Packets_for_Event_" + event

    if os.path.isdir(event_folder):
      shutil.rmtree(event_folder)
      os.makedirs(event_folder)
    else:
      os.makedirs(event_folder)
    return event_folder

# ZIP Progress Folders
def zip_event_folder(event_folder):
    shutil.make_archive(os.path.join(event_folder), 'zip', os.path.join(event_folder))
    shutil.rmtree(event_folder)

def download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar):
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    ssh_client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
    ftp_client=ssh_client.open_sftp()
    ftp_client.get(f"{i}/{year}/{month}/{day}.tgz", f"{event_folder}/{day}.tgz", callback=lambda x, y: download_zip_progress(x, y, root, progress_label_string, progress_bar))
    ftp_client.close()

# Label Functions
def download_zip_progress(x, y, root, progress_label_string, progress_bar):
    if x > 0:
        percentage = round(x / y * 100, 2)
        print(percentage)
        if percentage == 100.00:
            progress_label_string.set(f"Zip file has been downloaded")
            progress_bar["value"] = 0
            root.update()
        else:
            progress_label_string.set(f"Downloading zip file - Progress {percentage}%")
            progress_bar["value"] = percentage
            root.update()

def download_files_progress(x, y, root, progress_label_string, progress_bar):
    if x > 0:
        percentage = round(x / y * 100, 2)
        if percentage == 100.00:
            progress_label_string.set(f"All files have been downloaded.")
            progress_bar["value"] = 0
            root.update()
        else:
            progress_label_string.set(f"Downloaded {percentage}% of files.")
            progress_bar["value"] = percentage
            root.update()

def zipped_files_checked_progress(x, y, root, progress_label_string, progress_bar, feed_event_id):
    if x > 0:
        percentage = round(x / y * 100, 2)
        print(percentage)
        if percentage == 100.00:
            progress_bar["value"] = 0
            progress_label_string.set(f"All files have been checked and verified")
            root.update()
        else:
            progress_label_string.set(f"Checking files for feed_event_id {feed_event_id}. {percentage}% of files checked")
            progress_bar["value"] = percentage
            root.update()

def verify_files_pulled(x, y, root, progress_label_string, progress_bar):
    if x > 0:
            percentage = round(x / y * 100, 2)
            print(percentage)
            if percentage == 100.00:
                progress_label_string.set(f"All files have been checked and verified")
                progress_bar["value"] = 0
                root.update()
            else:
                progress_label_string.set(f"Verifying files pulled from zips. {percentage}% of files checked")
                progress_bar["value"] = percentage
                root.update()

def events_finished(x, y, root, total_progress_label_string, total_progress_bar):
    percentage = round(x / y * 100, 2)
    total_progress_label_string.set(f"Total Progress: Event {x} of {y}")
    total_progress_bar["value"] = percentage
    root.update()

# Supplier Specific Functions
def lsport_download_folders(supplier, host, feed_event_id, event_folder, username, password, folder_one_verify, folder_two_verify, chosen_directories, root, progress_label_string, progress_bar):
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    ssh_client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
    ftp_client=ssh_client.open_sftp()
    try:
        print("Try first folder structure")
        for filename in ftp_client.listdir(folder_one_verify):
            ftp_client.get(f"{folder_one_verify}/{filename}", os.path.join(event_folder, filename), callback=lambda x, y: download_files_progress(x, y, root, progress_label_string, progress_bar))
    except FileNotFoundError:
        print("First folder structure failed - Trying second structure.")
        try:
            for filename in ftp_client.listdir(folder_two_verify):
                ftp_client.get(f"{folder_two_verify}/{filename}", os.path.join(event_folder, filename), callback=lambda x, y: download_files_progress(x, y, root, progress_label_string, progress_bar))
        except FileNotFoundError:
            print("Folder does not exist - please double check the event")

    if len(feed_event_id) > 7:
        feed_event_id = feed_event_id[0:7]

    for i in chosen_directories:
        for filename in ftp_client.listdir(i):
            print(f"Checking {filename}")
            ftp_client.get(f"{i}/{filename}", os.path.join(event_folder, filename), callback=lambda x, y: verify_files_pulled(x, y, root, progress_label_string, progress_bar))
            opened_file = open(os.path.join(event_folder, filename), "r")
            read_opened_file = opened_file.read()
            pattern = re.search(str('"FixtureId":' + " " + feed_event_id), str(read_opened_file))
            if pattern != None:
                read_opened_file = opened_file.close()
                os.rename(os.path.join(event_folder, filename), os.path.join(event_folder, "1_" + filename))
            else:
                read_opened_file = opened_file.close()
                os.remove(os.path.join(event_folder, filename))

def sportsradar_download_folders(supplier, host, feed_event_id, event_folder, chosen_directories, username, password, root, progress_label_string, progress_bar):
    feed_event_id_folder = f"sr_match{feed_event_id[-8:]}"
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    ssh_client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
    ftp_client=ssh_client.open_sftp()
    for i in chosen_directories:
        try:
            for filename in ftp_client.listdir(f"{i}/{feed_event_id_folder}"):
                ftp_client.get(f"{i}/{feed_event_id_folder}/{filename}", os.path.join(event_folder, filename), callback=lambda x, y: download_files_progress(x, y, root, progress_label_string, progress_bar))
        except IOError:
            print("Remote Folder not in this directory")