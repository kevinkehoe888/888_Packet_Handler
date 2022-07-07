from datetime import date, timedelta, datetime

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
    ]
]

supplier_available_dates = [
    [datetime.strptime('2020-08-31', '%Y-%m-%d').date(), (date.today() - timedelta(days = 1))],
    [datetime.strptime('2020-09-29', '%Y-%m-%d').date(), (date.today() - timedelta(days = 1))],
    [datetime.strptime('2020-04-29', '%Y-%m-%d').date(), (date.today())], #  - timedelta(days = 1)
    [datetime.strptime('2020-04-29', '%Y-%m-%d').date(), (date.today())], #  - timedelta(days = 1)
    [datetime.strptime('2020-04-29', '%Y-%m-%d').date(), (date.today())], # - timedelta(days = 1)
    [datetime.strptime('2020-08-17', '%Y-%m-%d').date(), datetime.strptime('2020-10-31', '%Y-%m-%d').date()],
    [datetime.strptime('2020-08-17', '%Y-%m-%d').date(), datetime.strptime('2020-11-30', '%Y-%m-%d').date()],
    [datetime.strptime('2020-04-29', '%Y-%m-%d').date(), (date.today() - timedelta(days = 1))],
    [datetime.strptime('2020-04-29', '%Y-%m-%d').date(), (date.today() - timedelta(days = 1))],
    [datetime.strptime('2020-04-29', '%Y-%m-%d').date(), (date.today() - timedelta(days = 1))]
]

def choose_supplier_directories(supplier):
    return supplier_remote_folders[supplier]

def choose_supplier_dates(supplier):
    return supplier_available_dates[supplier]