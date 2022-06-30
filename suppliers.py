import os
import re
import shutil
import tarfile
import universal_functions
import json
from bs4 import BeautifulSoup

def lsports_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("LSPORTS")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        folder_one_verify = f"/mnt/feeds_data/fi_lsports_connector/{feed_event_id}"
        folder_two_verify = f"/mnt/feeds_data/fi_lsports_connector/{year}/{month}/{day}/{feed_event_id}"

        universal_functions.lsport_download_folders(supplier, host, feed_event_id, event_folder, username, password, folder_one_verify, folder_two_verify, chosen_directories, root, progress_label_string, progress_bar)

    universal_functions.zip_event_folder(event_folder)

def sportsradar_packets(supplier, host, feed_event_id, event_folder, chosen_directories, username, password, root, progress_label_string, progress_bar):
    print("SPORTSRADAR")
    print(chosen_directories)
    universal_functions.sportsradar_download_folders(supplier, host, feed_event_id, event_folder, chosen_directories, username, password, root, progress_label_string, progress_bar)
    universal_functions.zip_event_folder(event_folder)

def metric_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("METRIC")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)

            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                f = tar.extractfile(member)
                if f is not None:
                    pattern = re.search(str(feed_event_id), str(f.read()))
                    if pattern != None:
                        files.append(member)
                        print(member)

            tar.extractall(path = event_folder, members=files)
            tar.close()

            if os.path.exists(f"{event_folder}/{day}"):
                files_list = os.listdir(f"{event_folder}/{day}")
                for files in files_list:
                    shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
                shutil.rmtree(f"{event_folder}/{day}")
                os.remove(f"{event_folder}/{day}.tgz")
            else:
                os.remove(f"{event_folder}/{day}.tgz")

    non_event_files = []
    for i in os.listdir(event_folder):
        print(i)
        if ".json" in str(i):
            f = open(f"{event_folder}/{i}")
            content = json.loads(f.read())
            feed_id_match = False
            if content["eventId"] == feed_event_id:
                feed_id_match = True
            if feed_id_match == True:
                print("KEEPING JSON FILE")
                f.close()
            else:
                print("REMOVING JSON FILE")
                f.close()
                non_event_files.append(str(i))

    for files in non_event_files:
        print(f"REMOVING {files}")
        os.remove(os.path.join(event_folder, str(files)))
    
    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)

def press_association_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("PA")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)

            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                f = tar.extractfile(member)
                if f is not None:
                    pattern = re.search(str(feed_event_id), str(f.read()))
                    if pattern != None:
                        files.append(member)
                        print(member)

            tar.extractall(path = event_folder, members=files)
            tar.close()

            if os.path.exists(f"{event_folder}/{day}"):
                files_list = os.listdir(f"{event_folder}/{day}")
                for files in files_list:
                    shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
                shutil.rmtree(f"{event_folder}/{day}")
                os.remove(f"{event_folder}/{day}.tgz")
            else:
                os.remove(f"{event_folder}/{day}.tgz")
    
    non_event_files = []
    for i in os.listdir(event_folder):
        print(i)
        if ".xml" in str(i):
            f = open(f"{event_folder}/{i}")
            soup = BeautifulSoup(f.read(), 'xml')
            race_tag = soup.find_all('Race')
            raceNumber_match = False
            for i in race_tag:
                if i["id"] == feed_event_id:
                    print("PA FOUND FILE WOOOO")
                    raceNumber_match = True
                    break

            if raceNumber_match == True:
                print("KEEPING XML FILE")
                f.close()
            else:
                print("REMOVING JSON FILE")
                f.close()
                non_event_files.append(str(i))
    
    for files in non_event_files:
        print(f"REMOVING {files}")
        os.remove(os.path.join(event_folder, str(files)))

    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)

def dogs_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("PAGH")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)

            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                f = tar.extractfile(member)
                if f is not None:
                    if ".xml" in str(member):
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

            tar.extractall(path = event_folder, members=files)
            tar.close()

            if os.path.exists(f"{event_folder}/{day}"):
                files_list = os.listdir(f"{event_folder}/{day}")
                for files in files_list:
                    shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
                shutil.rmtree(f"{event_folder}/{day}")
                os.remove(f"{event_folder}/{day}.tgz")
            else:
                os.remove(f"{event_folder}/{day}.tgz")

        #for i in chosen_directories:
            #print(f"{i}/{year}/{month}/{day}.tgz")
            #universal_functions.download_filter_day(supplier, host, feed_event_id, f"{event_folder}/{day}.tgz", event_folder, f"{i}/{year}/{month}/{day}.tgz", username, password, day)
    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)

def betradar_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("Betradar")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)

            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                f = tar.extractfile(member)
                if f is not None:
                    if ".xml" in str(member):
                        soup = BeautifulSoup(f.read(), 'xml')
                        match_tag = soup.find_all('Match')
                        BetradarMatchID_match = False
                        for i in match_tag:
                            if i["BetradarMatchID"] == feed_event_id:
                                BetradarMatchID_match = True
                                break
                        if BetradarMatchID_match == True:
                            files.append(member)

            tar.extractall(path = event_folder, members=files)
            tar.close()

            if os.path.exists(f"{event_folder}/{day}"):
                files_list = os.listdir(f"{event_folder}/{day}")
                for files in files_list:
                    shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
                shutil.rmtree(f"{event_folder}/{day}")
                os.remove(f"{event_folder}/{day}.tgz")
            else:
                os.remove(f"{event_folder}/{day}.tgz")

    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)

def betradar_inplay_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("Betradar Inplay")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)

            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                root.update()
                f = tar.extractfile(member)
                if f is not None:
                    if ".xml" in str(member):
                        soup = BeautifulSoup(f.read(), 'xml')
                        match_tag = soup.find_all('Match')
                        BetradarMatchID_match = False
                        for i in match_tag:
                            if i["matchid"] == feed_event_id:
                                BetradarMatchID_match = True
                                break
                        if BetradarMatchID_match == True:
                            files.append(member)

            tar.extractall(path = event_folder, members=files)
            tar.close()

            root.update()
            if os.path.exists(f"{event_folder}/{day}"):
                files_list = os.listdir(f"{event_folder}/{day}")
                for files in files_list:
                    shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
                shutil.rmtree(f"{event_folder}/{day}")
                os.remove(f"{event_folder}/{day}.tgz")
            else:
                os.remove(f"{event_folder}/{day}.tgz")
            root.update()
    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)

def sporting_solutions_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("SPORTING SOLUTIONS")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)

            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                f = tar.extractfile(member)
                if f is not None:
                    if ".json" in str(member):
                        if feed_event_id in str(member):
                            print("MATCHING JSON FILE")
                            files.append(member)

            tar.extractall(path = event_folder, members=files)
            tar.close()

            for path, subdirs, files in os.walk(f"{event_folder}"):
                for name in files:
                    shutil.move(os.path.join(path, name), os.path.join(event_folder, name))
            shutil.rmtree(f"{event_folder}/{day}")
            os.remove(f"{event_folder}/{day}.tgz")

    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)

def sporting_solutions_inplay_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("SPORTING SOLUTIONS INPLAY")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)

            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                f = tar.extractfile(member)
                if f is not None:
                    if ".json" in str(member):
                        if feed_event_id in str(member):
                            print("MATCHING JSON FILE")
                            files.append(member)

            tar.extractall(path = event_folder, members=files)
            tar.close()

            for path, subdirs, files in os.walk(f"{event_folder}"):
                for name in files:
                    shutil.move(os.path.join(path, name), os.path.join(event_folder, name))
            shutil.rmtree(f"{event_folder}/{day}")
            os.remove(f"{event_folder}/{day}.tgz")

    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)
    
def betgenius_inplay_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password, root, progress_label_string, progress_bar):
    print("BETGENIUS INPLAY")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_zip_folder(host, username, password, i, year, month, day, event_folder, root, progress_label_string, progress_bar)
            root.update()
            tar = tarfile.open(f"{event_folder}/{day}.tgz", "r:gz")
            root.update()
            # This list will be used to store any files that have been found with the pattern needed.
            files = []
            for index, member in enumerate(tar.getmembers()):
                universal_functions.zipped_files_checked_progress(index + 1, len(tar.getmembers()), root, progress_label_string, progress_bar, feed_event_id)
                root.update()
                f = tar.extractfile(member)
                if f is not None:
                    pattern = re.search(str(feed_event_id), str(f.read()))
                    if pattern != None:
                        files.append(member)
                        print(member)
                root.update()
            tar.extractall(path = event_folder, members=files)
            tar.close()
            root.update()
            if os.path.exists(f"{event_folder}/{day}"):
                files_list = os.listdir(f"{event_folder}/{day}")
                for files in files_list:
                    shutil.move(os.path.join(f"{event_folder}/{day}", files), os.path.join(event_folder, files))
                shutil.rmtree(f"{event_folder}/{day}")
                os.remove(f"{event_folder}/{day}.tgz")
            else:
                os.remove(f"{event_folder}/{day}.tgz")
            root.update()
    non_event_files = []
    for num, i in enumerate(os.listdir(event_folder)):
        universal_functions.verify_files_pulled(num + 1, len(os.listdir(event_folder)), root, progress_label_string, progress_bar)
        root.update()
        if ".json" in str(i):
            f = open(f"{event_folder}/{i}")
            content = json.load(f)
            content2 = json.loads(content['content'])
            feed_id_match = False
            for value in content2:
                if value == "BetgeniusFixtureId":
                    if str(content2[value]) == feed_event_id:
                        feed_id_match = True
                        break
                elif value == "FixtureId":
                    if str(content2[value]) == feed_event_id:
                        feed_id_match = True
                        break
            if feed_id_match == True:
                print("KEEPING JSON FILE")
                f.close()
            else:
                print("REMOVING JSON FILE")
                f.close()
                non_event_files.append(str(i))

        elif ".xml" in str(i):
            f = open(f"{event_folder}/{i}")
            soup = BeautifulSoup(f, 'xml')
            FixtureId, Id = soup.find_all('FixtureId'), soup.find_all('Id')
            feed_id_match = False
            for g in FixtureId:
                if g.text == feed_event_id:
                    feed_id_match = True
                    break

            for g in Id:
                if g.text == feed_event_id:
                    feed_id_match = True
                    break

            if feed_id_match == True:
                print("KEEPING XML FILE")
                StartTimeUtc = len(soup.find_all('StartTimeUtc'))
                if StartTimeUtc > 0:
                    print("START TIME UTC FOUND: RENAIMING WITH 1_")
                    f.close()
                    os.rename(os.path.join(event_folder, str(i)), os.path.join(event_folder + "/1_" + str(i)))
                else:
                    f.close()
            else:
                print("REMOVING XML FILE")
                f.close()
                non_event_files.append(str(i))
    root.update()
    for files in non_event_files:
        print(f"REMOVING {files}")
        os.remove(os.path.join(event_folder, str(files)))
    root.update()
    # Zipped Event Folder and Remove it to save space
    universal_functions.zip_event_folder(event_folder)

supplier_functions = [
    lsports_packets,
    sportsradar_packets,
    metric_packets,
    press_association_packets,
    dogs_packets,
    betradar_packets,
    betradar_inplay_packets,
    sporting_solutions_packets,
    sporting_solutions_inplay_packets,
    betgenius_inplay_packets
]