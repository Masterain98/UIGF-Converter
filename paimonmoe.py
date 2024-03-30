import time
import datetime

import pandas as pd
import json
import requests
from utils import get_uigf_gacha_type_online


def type_translate(x: str) -> str:
    if x == "Weapon":
        return "武器"
    elif x == "Character":
        return "角色"
    else:
        return ""


def item_id_converter(x: str, item_dict: dict) -> int:
    if x in item_dict.keys():
        return item_dict[x]
    print("转换物品 ID 错误： " + x)
    return 0


def paimon_moe_UIGF_converter(file_name: str, uid: str, drop_six_month_data: bool = "y", timezone: int = 8):
    if timezone == -99:
        return None

    print("drop_six_month_data:", str(drop_six_month_data))

    # Convert Task
    print("正在转换文件： " + file_name)
    if file_name[0] == "\"":
        file_name = file_name.replace("\"", "")

    # Make dictionary
    item_dict = json.loads(requests.get("https://api.uigf.org/dict/genshin/en.json").text)
    """
    AvatarExcelConfigData = json.loads(
        requests.get("https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/ExcelBinOutput/AvatarExcelConfigData.json").text)
    WeaponExcelConfigData = json.loads(
        requests.get("https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/ExcelBinOutput/WeaponExcelConfigData.json").text)
    chs_dict = json.loads(
        requests.get("https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapCHS.json").text)
    en_dict = json.loads(
        requests.get("https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapEN.json").text)

    eng_to_chs_dict = {}
    item_list = [AvatarExcelConfigData, WeaponExcelConfigData]
    for this_list in item_list:
        for item in this_list:
            this_name_hash_id = item["nameTextMapHash"]
            try:
                eng_name = en_dict[str(this_name_hash_id)]
                chs_name = chs_dict[str(this_name_hash_id)]
                eng_to_chs_dict[eng_name] = chs_name
            except KeyError:
                continue
    """

    # 加载 Paimon.moe的祈愿导出Excel文件
    df1 = pd.read_excel(file_name, sheet_name="Character Event")
    df2 = pd.read_excel(file_name, sheet_name="Weapon Event")
    df3 = pd.read_excel(file_name, sheet_name="Standard")
    df4 = pd.read_excel(file_name, sheet_name="Beginners' Wish")

    # 角色活动祈愿
    # 翻译名称
    # df1["item_id"] = df1.Name.apply(lambda x: item_dict[x])
    #df1["name"] = df1.Name.apply(lambda x: eng_to_chs_dict[x])
    #df1.drop(columns=['Name'], inplace=True)
    # 翻译种类
    df1["item_type"] = df1.Type.apply(lambda x: type_translate(x))
    df1.drop(columns=['Type'], inplace=True)
    # 创建稀有度列
    df1["rank_type"] = df1["⭐"]
    df1.drop(columns=['⭐'], inplace=True)
    # 通过卡池信息判定gacha_type
    df1["gacha_type"] = df1.apply(lambda x: get_uigf_gacha_type_online(x, timezone), axis=1)
    df1.drop(columns=['Banner'], inplace=True)
    # 增加uigf_gacha_type列
    df1["uigf_gacha_type"] = str(301)

    # 武器活动祈愿
    # 翻译名称
    df2["item_id"] = df2.Name.apply(lambda x: item_id_converter(x, item_dict))
    #df2["name"] = df2.Name.apply(lambda x: eng_to_chs_dict[x])
    #df2.drop(columns=['Name'], inplace=True)
    # 翻译种类
    df2["item_type"] = df2.Type.apply(lambda x: type_translate(x))
    df2.drop(columns=['Type'], inplace=True)
    # 创建稀有度列
    df2["rank_type"] = df2["⭐"]
    df2.drop(columns=['⭐'], inplace=True)
    # 创建gacha_type列
    df2["gacha_type"] = str(302)
    df2["uigf_gacha_type"] = str(302)
    df2.drop(columns=['Banner'], inplace=True)

    # 常驻祈愿
    # 翻译名称
    df3["item_id"] = df3.Name.apply(lambda x: item_id_converter(x, item_dict))
    #df3["name"] = df3.Name.apply(lambda x: eng_to_chs_dict[x])
    #df3.drop(columns=['Name'], inplace=True)
    # 翻译种类
    df3["item_type"] = df3.Type.apply(lambda x: type_translate(x))
    df3.drop(columns=['Type'], inplace=True)
    # 创建稀有度列
    df3["rank_type"] = df3["⭐"]
    df3.drop(columns=['⭐'], inplace=True)
    # 创建gacha_type列
    df3["gacha_type"] = str(200)
    df3["uigf_gacha_type"] = str(200)
    df3.drop(columns=['Banner'], inplace=True)

    # 新手祈愿
    # 翻译名称
    df4["item_id"] = df4.Name.apply(lambda x: item_id_converter(x, item_dict))
    #df4["name"] = df4.Name.apply(lambda x: eng_to_chs_dict[x])
    #df4.drop(columns=['Name'], inplace=True)
    # 翻译种类
    #df4["item_type"] = df4.Type.apply(lambda x: type_translate(x))
    df4.drop(columns=['Type'], inplace=True)
    # 创建稀有度列
    df4["rank_type"] = df4["⭐"]
    df4.drop(columns=['⭐'], inplace=True)
    # 创建gacha_type列
    df4["gacha_type"] = str(100)
    df4["uigf_gacha_type"] = str(100)
    df4.drop(columns=['Banner'], inplace=True)

    # 连接DF
    MergedDF = [df1, df2, df3, df4]
    MergedDF = pd.concat(MergedDF)
    MergedDF.reset_index(inplace=True)
    MergedDF.drop(columns='index', inplace=True)
    # 删除无用列
    MergedDF["time"] = MergedDF["Time"]
    MergedDF.drop(columns=['Time'], inplace=True)
    MergedDF.sort_values(by=['time'], ascending=True, inplace=True)
    MergedDF.drop(columns=['Pity', '#Roll', 'Group'], inplace=True)
    # 添加杂项列
    MergedDF["uid"] = ""
    MergedDF["lang"] = "zh-cn"
    MergedDF["count"] = "1"
    MergedDF["id"] = ""
    # 创建id
    firstID = 1612303200000000000 - MergedDF.shape[0]
    MergedDF['id'] = firstID + MergedDF.index
    # 重置数据类型
    MergedDF['count'] = MergedDF['count'].astype(str)
    MergedDF['gacha_type'] = MergedDF['gacha_type'].astype(str)
    MergedDF['id'] = MergedDF['id'].astype(str)
    MergedDF['lang'] = MergedDF['lang'].astype(str)
    #MergedDF['name'] = MergedDF['name'].astype(str)
    MergedDF['item_id'] = MergedDF['item_id'].astype(str)
    MergedDF['rank_type'] = MergedDF['rank_type'].astype(str)
    MergedDF['time'] = MergedDF['time'].astype(str)
    MergedDF['uid'] = MergedDF['uid'].astype(str)
    MergedDF['uigf_gacha_type'] = MergedDF['uigf_gacha_type'].astype(str)
    # 修改列顺序
    #MergedDF = MergedDF[["count", "gacha_type", "id", "item_type", "lang", "name",
    #                     "rank_type", "time", "uid", "uigf_gacha_type"]]
    MergedDF = MergedDF[["count", "gacha_type", "id", "lang",
                         "rank_type", "time", "uid", "uigf_gacha_type"]]

    # 删除近6个月的数据
    if drop_six_month_data:
        MergedDF['time'] = pd.to_datetime(MergedDF['time'])
        deadline_time = datetime.datetime.now() - datetime.timedelta(days=180)
        MergedDF = MergedDF[MergedDF['time'] < deadline_time]
        MergedDF['time'] = MergedDF['time'].astype(str)
    else:
        pass

    # 创建 UIGF Excel
    # new_file_name = "uigf_" + uid + ".xlsx"
    # MergedDF.to_excel(new_file_name, sheet_name='原始数据', index=False)

    # 创建 UIGF JSON
    json_output = {
        "info": {
            "uid": uid,
            "lang": "zh-cn",
            "export_timestamp": int(time.time()),
            "export_app": "Paimon.moe-WishHistory-UIGF-Exporter",
            "export_app_version": "1.0.0",
            "uigf_version": "v2.3"
        }
    }
    output_list = []
    for index, row in MergedDF.iterrows():
        this_row_data = {
            "uigf_gacha_type": row["uigf_gacha_type"],
            "gacha_type": row["gacha_type"],
            "count": row["count"],
            "time": row["time"],
            "rank_type": row["rank_type"],
            "id": row["id"]
        }
        output_list.append(this_row_data)
    json_output["list"] = output_list
    with open("uigf_" + uid + ".json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=4)
