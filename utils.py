from datetime import datetime, timedelta
import httpx
import pytz

banner_data = httpx.get("https://raw.githubusercontent.com/Masterain98/Genshin-Wish-Event-History-Data/main/pool.json").json()


def get_uigf_gacha_type_online(row, utc_offset_value: int) -> int:
    target_time_zone = pytz.timezone(f"Etc/GMT{utc_offset_value}" if utc_offset_value < 0
                                     else f"Etc/GMT+{utc_offset_value}")
    gacha_time = datetime.strptime(row["Time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=target_time_zone)
    banner_name = row["Banner"].replace("'", "")
    gacha_type = 0
    for banner in banner_data:
        start_time = datetime.strptime(banner["start_time"],
                                       "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone("Asia/Shanghai"))
        end_time = datetime.strptime(banner["end_time"],
                                     "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone("Asia/Shanghai"))
        if banner_name == banner["localization"]["EN"]["pool_title"].replace("'", ""):
            # print(f"Found matched name: {banner_name}, from {start_time} to {end_time}")
            if banner["order"] >= 2 and utc_offset_value != 8:
                offset_hours = 8 - utc_offset_value
                start_time = start_time + timedelta(hours=offset_hours)
                end_time = end_time + timedelta(hours=offset_hours)
            if start_time < gacha_time.astimezone(pytz.timezone("Asia/Shanghai")) < end_time:
                gacha_type = banner["uigf_type"]
                break
    if gacha_type == 0:
        print(banner_name + " is not a recognized banner, contact developer to request update\n"
                            "┕-->> gacha time (UTC+8): " + str(gacha_time.astimezone(pytz.timezone("Asia/Shanghai")))
              + "\n" + "┕-->> gacha time (Local): " + str(gacha_time))

    return gacha_type


def get_utc_int_from_sever(server_name: str) -> int:
    server_name = server_name.lower()
    china_server = ["china", "cn"]
    america_server = ["america", "na", "north america"]
    europe_server = ["europe", "eu"]
    asia_server = ["asia", "sea", "southeast asia", "jp", "kr"]
    sar_server = ["sar", "tw/hk/mo", "tw", "hk", "mo"]
    server_utc = -99
    if server_name in china_server:
        server_utc = 8
    elif server_name in america_server:
        server_utc = -5
    elif server_name in europe_server:
        server_utc = 1
    elif server_name in asia_server:
        server_utc = 8
    elif server_name in sar_server:
        server_utc = 8
    if server_utc == -99:
        print("Server name not recognized, please check again")
    else:
        print("Using UTC " + str(server_utc))
    return server_utc
