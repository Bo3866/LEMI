# ==============================
# A1 交通事故資料
# ==============================

from data_fetch.json_api import fetch_json


# ==============================
# A1 政府資料 API
# ==============================

A1_JSON_URL = (
    "https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/"
    "dataset/F4077949-50CC-4640-8114-79958CC8BBEA/"
    "resource/BDF579BD-CD16-469F-BDA6-A9637847402C/download"
)


# ==============================
# 取得 A1 原始資料
# ==============================

def fetch_a1_data():
    """
    從政府 API 取得 A1 交通事故原始資料。

    回傳：
        list[dict]
    """

    data = fetch_json(
        A1_JSON_URL,
        verify_ssl=False
    )

    records = data.get("result", {}).get("records", [])

    if not isinstance(records, list):
        raise ValueError(
            "A1 API 回傳格式不是 records list"
        )

    return records


# ==============================
# 篩選 A1
# ==============================

def filter_a1(records):
    """
    從事故資料中只保留事故類別名稱為 A1 的資料。
    """

    return [
        record
        for record in records
        if record.get("事故類別名稱") == "A1"
    ]


# ==============================
# 取得經緯度
# ==============================

def parse_coordinates(record):
    """
    從事故資料取得經緯度。

    回傳：
        (lat, lng)

    如果沒有有效座標，回傳：
        (None, None)
    """

    try:
        lat = float(record.get("緯度"))
        lng = float(record.get("經度"))
    except (TypeError, ValueError):
        return None, None

    return lat, lng


# ==============================
# 建立事故 ID
# ==============================

def make_accident_id(record, lat, lng):
    """
    根據事故日期、時間與座標建立事故 ID。

    用來判斷是否為重複事故。
    """

    return "_".join([
        str(record.get("發生年度", "")),
        str(record.get("發生日期", "")),
        str(record.get("發生時間", "")),
        f"{lat:.6f}",
        f"{lng:.6f}"
    ])


# ==============================
# 整理單筆事故資料
# ==============================

def normalize_a1_record(record):
    """
    將政府原始 A1 資料整理成系統使用的格式。
    """

    lat, lng = parse_coordinates(record)

    if lat is None or lng is None:
        return None

    accident_id = make_accident_id(
        record,
        lat,
        lng
    )

    return {
        "id": accident_id,

        "year": record.get("發生年度"),
        "month": record.get("發生月份"),
        "date": record.get("發生日期"),
        "time": record.get("發生時間"),

        "lat": lat,
        "lng": lng,

        "location": record.get("發生地點"),

        "weather": record.get("天候名稱"),
        "light": record.get("光線名稱"),

        "roadType": record.get(
            "道路類別-第1當事者-名稱"
        ),

        "speedLimit": record.get(
            "速限-第1當事者"
        ),

        "accidentType": record.get(
            "事故類別名稱"
        ),

        "accidentSubType": record.get(
            "事故類別名稱-第1當事者"
        )
    }


# ==============================
# 去除重複事故
# ==============================

def deduplicate_a1(records):
    """
    去除重複的 A1 事故。

    判斷依據：
        year + date + time + lat + lng
    """

    unique_records = {}
    invalid_count = 0

    for record in records:

        normalized = normalize_a1_record(
            record
        )

        if normalized is None:
            invalid_count += 1
            continue

        accident_id = normalized["id"]

        if accident_id not in unique_records:
            unique_records[accident_id] = normalized

    return list(unique_records.values())


# ==============================
# 完整取得 A1 資料
# ==============================

def get_a1_accidents():
    """
    完整取得並整理 A1 交通事故資料。

    流程：

        政府 API
            ↓
        篩選 A1
            ↓
        座標檢查
            ↓
        資料格式整理
            ↓
        去除重複
            ↓
        回傳
    """

    records = fetch_a1_data()

    a1_records = filter_a1(
        records
    )

    accidents = deduplicate_a1(
        a1_records
    )

    return accidents


# ==============================
# 測試
# ==============================

if __name__ == "__main__":

    accidents = get_a1_accidents()

    print(
        f"A1 事故資料共有 {len(accidents)} 筆"
    )

    if accidents:
        print("第一筆資料：")
        print(accidents[0])