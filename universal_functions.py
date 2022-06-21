from cgitb import text
import os
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
                    content = json.loads(f.read())
                    content2 = json.loads(content['content'])
                    for value in content2:
                        if value == "BetgeniusFixtureId":
                            if str(content2[value]) == feed_event_id:
                                print("MATCHING JSON FILE")
                                files.append(member)
                                break
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
                    soup = BeautifulSoup(f.read(), 'xml')
                    FixtureId, Id = soup.find_all('FixtureId'), soup.find_all('Id')
                    feed_id_match = False
                    for i in FixtureId:
                        if i.text == feed_event_id:
                            print("MATCHING XML FILE on FixtureId Tag")
                            feed_id_match = True
                            break

                    for i in Id:
                        if i.text == feed_event_id:
                            print("MATCHING XML FILE on Id Tag")
                            feed_id_match = True
                            break

                    if feed_id_match == True:
                        files.append(member)
        
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

def progress(transferred: int, tobe_transferred: int):
    print(f"\033[F\r\033[KFile is {round(int(transferred/1024) / int(tobe_transferred/1024) * 100, 2)}% Downloaded")