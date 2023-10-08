import json
import time
import requests

import utils
from paimonmoe import paimon_moe_UIGF_converter

GACHA_TYPE_CONVERTER = {
    "100": "100",
    "200": "200",
    "301": "301",
    "400": "301",
    "302": "302"
}


def teyvat_assistant_record_to_UIGF_format(json_file_name: str):
    record = open(json_file_name).read()
    record = json.loads(record)
    record_keys = list(record.keys())
    record_keys.remove("timestamp")

    # Find out all UID
    UID_list = []
    for key in record_keys:
        gacha_record = record[key]
        this_gacha_record_uid_list = list(set([gacha["uid"] for gacha in gacha_record]))
        UID_list += this_gacha_record_uid_list
    UID_list = list(set(UID_list))
    print(UID_list)

    for uid in UID_list:
        data_list = []
        for this_gacha_type in record_keys:
            for gacha_record in record[this_gacha_type]:
                this_gacha_info = {
                    "gacha_type": gacha_record["gacha_type"],
                    "uigf_gacha_type": GACHA_TYPE_CONVERTER[gacha_record["gacha_type"]],
                    "item_id": "",
                    "count": "1",
                    "time": gacha_record["time"],
                    "name": gacha_record["name"],
                    "item_type": gacha_record["item_type"],
                    "rank_type": gacha_record["rank_type"],
                    "id": gacha_record["id"]
                }
                data_list.append(this_gacha_info)
        this_output = {
            "info": {
                "uid": uid,
                "lang": "zh-cn",
                "export_timestamp": int(time.time()),
                "export_app": "UIGF Converter - 提瓦特小助手",
                "export_app_version": "0.1",
                "uigf_version": "v2.3"
            },
            "list": data_list
        }
        with open(uid + ".json", "w", encoding="utf-8") as json_file:
            json.dump(this_output, json_file, indent=4, ensure_ascii=False)


def UIGF_valid(uigf_json_file: str):
    # Initial value
    valid_count = 0
    valid_data = []
    known_bad_name = []
    known_good_name = []

    # Read file
    record = open(uigf_json_file, encoding="utf-8").read()
    record = json.loads(record)
    record_info = record["info"]
    record_data = record["list"]

    # Handle data
    for data in record_data:
        gacha_name = data["name"]
        if gacha_name in known_bad_name:
            print("Not found: " + gacha_name + " @ " + data["time"])
        elif gacha_name in known_good_name:
            valid_data.append(data)
            valid_count += 1
        else:
            requests_result = requests.get("https://api.uigf.org/generic-translate/" + gacha_name)
            if requests_result.status_code == 200:
                valid_data.append(data)
                known_good_name.append(gacha_name)
                valid_count += 1
            elif requests_result.status_code == 404:
                print("Not found: " + gacha_name + " @ " + data["time"])
                known_bad_name.append(gacha_name)
            else:
                print("Error " + str(requests_result.status_code) + " : " + gacha_name)
                known_bad_name.append(gacha_name)
    print("Valid count: " + str(valid_count) + "/" + str(len(record_data)))

    # Output
    this_output = {
        "info": record_info,
        "list": valid_data
    }
    with open(uigf_json_file.replace(".json", "_valid.json"), "w", encoding="utf-8") as json_file:
        json.dump(this_output, json_file, indent=4, ensure_ascii=False)


def reset_index(uigf_json_file: str):
    # Read file
    record = open(uigf_json_file, encoding="utf-8").read()
    record = json.loads(record)
    info = record["info"]
    data_list = record["list"]

    first_record = 1612303200000000000 - len(record["list"])
    new_list = []
    for record in data_list:
        record["id"] = first_record
        first_record += 1
        new_list.append(record)
    # new_list.reverse()
    new_record = {
        "info": info,
        "list": new_list
    }
    with open(uigf_json_file.replace(".json", "_indexreset.json"), "w", encoding="utf-8") as json_file:
        json.dump(new_record, json_file, indent=4, ensure_ascii=False)

    # ./externalData/101023031.json


if __name__ == "__main__":
    # teyvat_assistant_record_to_UIGF_format("抽卡记录.json")
    # UIGF_valid("199036533_20231282043.json")
    # paimon_moe_UIGF_converter("externalData/paimonmoe_wish_history.xlsx", "199036533", True)
    print("=" * 20)
    print("UIGF 数据转换工具")
    print("Version: beta 0.1")
    print("GitHub: https://github.com/Masterain98/UIGF-Converter")
    print("这个工具旨在将自定义的原神祈愿记录数据格式转化为 UIGF 标准格式")
    print("关于 UIGF 标准格式的更多信息，请访问 https://uigf.org/")
    print("=" * 20)
    print("1. 将提瓦特小助手的抽卡记录转换为 UIGF 标准格式（Json 数据源）")
    print("2. 将 Paimon.moe 的祈愿记录转换为 UIGF 标准格式（xlsx 数据源）")
    print("3. 验证 UIGF 数据文件的有效性（仅用于预期可用的数据文件无法导入时使用）")
    print("4. 重置 ID")
    user_input_feature = input("请输入数字以选择功能：")
    user_input_file = input("请输入文件路径或拖入文件：")
    print("=" * 20)
    print("正在处理，请稍候...")
    if user_input_file[0] == '"':
        fileName = user_input_file.replace('"', '')
    if user_input_feature == "1":
        teyvat_assistant_record_to_UIGF_format(user_input_file)
    elif user_input_feature == "2":
        paimon_moe_UIGF_converter(user_input_file, input("请输入 UID："),
                                  input("是否删除近6个月的数据以避免重复？默认放弃（y/n）") == "y",
                                  utils.get_utc_int_from_sever(input("请输入服务器名称：")))
    elif user_input_feature == "3":
        UIGF_valid(user_input_file)
    elif user_input_feature == "4":
        reset_index(user_input_file)
    else:
        print("输入错误！")
    print("输出文件已保存至当前目录")
    input("按回车键退出程序...")
