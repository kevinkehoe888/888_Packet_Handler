import universal_functions

supplier_remote_folders = [
    [
        "/mnt/feeds_data/fi_lsports_connector/markets_meta", 
        "/mnt/feeds_data/fi_lsports_connector/outright_league_markets_meta", 
        "/mnt/feeds_data/fi_lsports_connector/outright_leagues_meta", 
        "/mnt/feeds_data/fi_lsports_connector/outright_meta"
    ],
    [
        "/mnt/feeds_data/fi_sportradar_connector/1",
        "/mnt/feeds_data/fi_sportradar_connector/2",
        "/mnt/feeds_data/fi_sportradar_connector/3",
        "/mnt/feeds_data/fi_sportradar_connector/4",
        "/mnt/feeds_data/fi_sportradar_connector/5",
        "/mnt/feeds_data/fi_sportradar_connector/6",
        "/mnt/feeds_data/fi_sportradar_connector/12",
        "/mnt/feeds_data/fi_sportradar_connector/13",
        "/mnt/feeds_data/fi_sportradar_connector/16",
        "/mnt/feeds_data/fi_sportradar_connector/19",
        "/mnt/feeds_data/fi_sportradar_connector/20",
        "/mnt/feeds_data/fi_sportradar_connector/21",
        "/mnt/feeds_data/fi_sportradar_connector/22",
        "/mnt/feeds_data/fi_sportradar_connector/23",
        "/mnt/feeds_data/fi_sportradar_connector/24",
        "/mnt/feeds_data/fi_sportradar_connector/29",
        "/mnt/feeds_data/fi_sportradar_connector/31",
        "/mnt/feeds_data/fi_sportradar_connector/32",
        "/mnt/feeds_data/fi_sportradar_connector/34",
        "/mnt/feeds_data/fi_sportradar_connector/37",
        "/mnt/feeds_data/fi_sportradar_connector/109",
        "/mnt/feeds_data/fi_sportradar_connector/111",
        "/mnt/feeds_data/fi_sportradar_connector/137",
        "/mnt/feeds_data/fi_sportradar_connector/153",
        "/mnt/feeds_data/fi_sportradar_connector/195"
    ],
    [
        "/mnt/feeds_data/i-0bd644c5c4eb7964c/metric_connector/METRIC",
        "/mnt/feeds_data/i-05dbabedb7c00a400/metric_connector/METRIC"
    ],
    [
        "/mnt/feeds_data/i-02c9341646f83a3fc/feed_normalizer/AT_THE_RACES", 
        "/mnt/feeds_data/i-05e69aedb921eb3c1/feed_normalizer/AT_THE_RACES", 
        "/mnt/feeds_data/i-0570b41c2388f6bf6/feed_normalizer/AT_THE_RACES", 
        "/mnt/feeds_data/i-0744c3e5e81090143/feed_normalizer/AT_THE_RACES", 
        "/mnt/feeds_data/i-03230d6944a3b8bdc/feed_normalizer/AT_THE_RACES", 
        "/mnt/feeds_data/i-04819bf2455666cbe/feed_normalizer/AT_THE_RACES", 
        "/mnt/feeds_data/i-013525a6f4ea171e5/feed_normalizer/AT_THE_RACES", 
        "/mnt/feeds_data/i-069466a0fcbd99b48/feed_normalizer/AT_THE_RACES", 
    ],
    [
        "/mnt/feeds_data/i-02c9341646f83a3fc/feed_normalizer/RACING_UK", 
        "/mnt/feeds_data/i-05e69aedb921eb3c1/feed_normalizer/RACING_UK",  
        "/mnt/feeds_data/i-0570b41c2388f6bf6/feed_normalizer/RACING_UK",  
        "/mnt/feeds_data/i-0744c3e5e81090143/feed_normalizer/RACING_UK",  
        "/mnt/feeds_data/i-03230d6944a3b8bdc/feed_normalizer/RACING_UK",  
        "/mnt/feeds_data/i-04819bf2455666cbe/feed_normalizer/RACING_UK",  
        "/mnt/feeds_data/i-013525a6f4ea171e5/feed_normalizer/RACING_UK",  
        "/mnt/feeds_data/i-069466a0fcbd99b48/feed_normalizer/RACING_UK",
    ],
    [
        "/mnt/feeds_data/i-02c9341646f83a3fc/feed_normalizer/SIS", 
        "/mnt/feeds_data/i-05e69aedb921eb3c1/feed_normalizer/SIS",  
        "/mnt/feeds_data/i-0570b41c2388f6bf6/feed_normalizer/SIS",  
        "/mnt/feeds_data/i-0744c3e5e81090143/feed_normalizer/SIS",  
        "/mnt/feeds_data/i-03230d6944a3b8bdc/feed_normalizer/SIS",  
        "/mnt/feeds_data/i-04819bf2455666cbe/feed_normalizer/SIS",  
        "/mnt/feeds_data/i-013525a6f4ea171e5/feed_normalizer/SIS",
    ],
    [
        "/mnt/feeds_data/i-04819bf2455666cbe/feed_connector/CMT"
    ],
    [
        "/mnt/feeds_data/i-03230d6944a3b8bdc/feed_normalizer/PA"
    ],
    [
        "/mnt/feeds_data/i-0570b41c2388f6bf6/feed_normalizer/PAGH"
    ],
    [
        "/mnt/feeds_data/i-05e69aedb921eb3c1/feed_normalizer/BR"
    ],
    [
        "/mnt/feeds_data/i-05e69aedb921eb3c1/drivein/BRIN"
    ],
    [
        "/mnt/feeds_data/i-013525a6f4ea171e5/feed_normalizer/SSOL"
    ],
    [
        "/mnt/feeds_data/i-013525a6f4ea171e5/drivein/SSOLIN"
    ],
    [
        "/mnt/feeds_data/i-05dbabedb7c00a400/feed_connector/BGIN",
        "/mnt/feeds_data/i-0bd644c5c4eb7964c/feed_connector/BGIN"
    ],
    [
        "/mnt/feeds_data/i-05dbabedb7c00a400/feed_connector/BGIN_SC",
        "/mnt/feeds_data/i-0bd644c5c4eb7964c/feed_connector/BGIN_SC"
    ]
]


def choose_supplier_directories(supplier):
    return supplier_remote_folders[supplier]

def lsports_packets():
    print("LSPORTS")
def sportsradar_packets():
    print("SPORTSRADAR")

def metric_packets(supplier, host, feed_event_id, event_folder, chosen_directories, dates, username, password):
    print("METRIC")
    for index, value in enumerate(dates):
        year = value[0:4]
        month = value[5:7]
        day = value[8:10]

        for i in chosen_directories:
            universal_functions.download_filter_day(supplier, host, feed_event_id, f"{event_folder}/{day}.tgz", event_folder, f"{i}/{year}/{month}/{day}.tgz", username, password, day)

supplier_functions = [
    lsports_packets,
    sportsradar_packets,
    metric_packets
]