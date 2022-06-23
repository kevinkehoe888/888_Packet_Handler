import os
import re
import shutil
import tarfile
import paramiko
import suppliers
import json
from bs4 import BeautifulSoup

def create_folders(event):
    event_folder = os.path.abspath(os.path.dirname(__file__)) + "/Packets_for_Event_" + event
    if os.path.isdir(event_folder):
      shutil.rmtree(event_folder)
      os.makedirs(event_folder)
    else:
      os.makedirs(event_folder)
    return event_folder

def download_filter_day(supplier, host, feed_event_id, event_folder_zipped, event_folder, supplier_folder, username, password, day):
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys(filename=os.path.expanduser('~/.ssh/known_hosts'))
    ssh_client.connect(hostname=host, username=username, password=password, key_filename=os.path.expanduser('~/.ssh/id_rsa'))
    ftp_client=ssh_client.open_sftp()
    ftp_client.get(supplier_folder, event_folder_zipped, callback=progress)
    ftp_client.close()

    tar = tarfile.open(event_folder_zipped, "r:gz")
    # This list will be used to store any files that have been found with the pattern needed.
    files = []
    for index, member in enumerate(tar.getmembers()):
        print(f"\033[F\r\033[K{round(int(index + 1) / len(tar.getmembers()) * 100, 2)}% of files in folder checked.")
        f = tar.extractfile(member)
        if f is not None:
            content = f.read()
            if ".json" in str(member):
                if supplier == 2:
                    content = json.loads(f.read())
                    if content["eventId"] == feed_event_id:
                        print("MATCHING FILE")
                        files.append(member)
                if supplier in (11, 12):
                    if feed_event_id in str(member):
                        print("MATCHING JSON FILE")
                        files.append(member)
                    
                if supplier == 13:
                    pattern = re.search(str('"' + "FixtureId\\\\" + '"' + ':' + "\\\\" + '"' + feed_event_id + "\\\\" + '"'), str(content))
                    #pattern2 = re.search(str('"' + "BetgeniusFixtureId\\\\" + '"' + ':' + "\\\\" + '"' + feed_event_id + "\\\\" + '"'), str(content))
                    #pattern = re.search(str("BetgeniusFixtureId=" + '"' + feed_event_id + '"'), str(content))
                    if pattern != None:
                        files.append(member)
                        print(member)
                    
                    #if pattern2 != None:
                        #files.append(member)
                        #print(member)

                    # content = json.loads(f.read())
                    # content2 = json.loads(content['content'])
                    # for value in content2:
                    #     if value == "BetgeniusFixtureId":
                    #         if str(content2[value]) == feed_event_id:
                    #             print("MATCHING JSON FILE")
                    #             files.append(member)
                    #             break
            elif ".xml" in str(member):
                if supplier == 7:
                    soup = BeautifulSoup(f.read(), 'xml')
                    race_tag = soup.find_all('Race')
                    raceNumber_match = False
                    for i in race_tag:
                        if i["id"] == feed_event_id:
                            print("PA FOUND FILE WOOOO")
                            raceNumber_match = True
                            break

                    if raceNumber_match == True:
                        files.append(member)

                if supplier == 8:
                    soup = BeautifulSoup(f.read(), 'xml')
                    meeting_tag, race_tag = soup.find_all('Meeting'), soup.find_all('Race')
                    raceNumber_match = False
                    for i in meeting_tag:
                        if i["meetingId"] == feed_event_id[:6]:
                            raceNumberId = feed_event_id[6:8]
                            if int(raceNumberId) >= 10:
                                raceNumberId = feed_event_id[6:8]
                            else:
                                raceNumberId = feed_event_id[7:8]
                            for j in race_tag:
                                if j["raceNumber"] == raceNumberId:
                                    raceNumber_match = True
                                    break

                    if raceNumber_match == True:
                        files.append(member)
                # Match BetradarMatchID - 9
                # Match matchid="23166981"- 10
                if supplier == 9:
                    soup = BeautifulSoup(f.read(), 'xml')
                    match_tag = soup.find_all('Match')
                    BetradarMatchID_match = False
                    for i in match_tag:
                        if i["BetradarMatchID"] == feed_event_id:
                            BetradarMatchID_match = True
                            break
                    if BetradarMatchID_match == True:
                        files.append(member)

                if supplier == 10:
                    soup = BeautifulSoup(f.read(), 'xml')
                    match_tag = soup.find_all('Match')
                    BetradarMatchID_match = False
                    for i in match_tag:
                        if i["matchid"] == feed_event_id:
                            BetradarMatchID_match = True
                            break
                    if BetradarMatchID_match == True:
                        files.append(member)

                if supplier == 13:
                    #print(content)
                    pattern = re.search("<FixtureId>" + feed_event_id + "</FixtureId>", str(content))
                    #pattern2 = re.search("<Id>" + feed_event_id + "</Id>", str(content))
                    if pattern != None:
                        files.append(member)
                    #if pattern2 != None:
                        #files.append(member)
                    # soup = BeautifulSoup(f.read(), 'xml')
                    # FixtureId, Id = soup.find_all('FixtureId'), soup.find_all('Id')
                    # feed_id_match = False
                    # for i in FixtureId:
                    #     if i.text == feed_event_id:
                    #         print("MATCHING XML FILE on FixtureId Tag")
                    #         feed_id_match = True
                    #         break

                    # for i in Id:
                    #     if i.text == feed_event_id:
                    #         print("MATCHING XML FILE on Id Tag")
                    #         feed_id_match = True
                    #         break

                    # if feed_id_match == True:
                    #     files.append(member)
        
    tar.extractall(path = event_folder, members=files)
    tar.close()
    
    if supplier not in (11,12):
        if os.path.exists(f"{event_folder}/{day}"):
            files_list = os.listdir(f"{event_folder}/{day}")
            for files in files_list:
                shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
            shutil.rmtree(f"{event_folder}/{day}")
            os.remove(event_folder_zipped)
        else:
            os.remove(event_folder_zipped)
    else:
        for path, subdirs, files in os.walk(f"{event_folder}"):
            for name in files:
                shutil.move(os.path.join(path, name), os.path.join(event_folder, name))
        shutil.rmtree(f"{event_folder}/{day}")
        os.remove(event_folder_zipped)

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


def progress(transferred: int, tobe_transferred: int):
    print(f"\033[F\r\033[KFile is {round(int(transferred/1024) / int(tobe_transferred/1024) * 100, 2)}% Downloaded")