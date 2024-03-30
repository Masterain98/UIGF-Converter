import json
import time

GACHA_TYPE_CONVERTER = {
    "100": "100",
    "200": "200",
    "301": "301",
    "400": "301",
    "302": "302"
}


def record_to_UIGF_format(json_file_name: str):
    with open(json_file_name, encoding="utf-8") as f:
        record = json.load(f)
    record_keys = list(record["info"].keys())
    record_keys.remove("export_timestamp")

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
