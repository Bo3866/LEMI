import re

from data_fetch.csv_api import (
    fetch_page,
    fetch_csv
)


# ======================================
# 政府毒品犯罪資料集
# ======================================

DRUG_DATASET_PAGE = (
    "https://data.gov.tw/dataset/57268"
)


# ======================================
# 找政府 CSV API URL
# ======================================

DRUG_URL_PATTERN = (
    r'https?://opdadm\.moi\.gov\.tw/'
    r'api/v1/no-auth/resource/api/'
    r'dataset/'
    r'([0-9A-Fa-f-]{36})/'
    r'resource/'
    r'([0-9A-Fa-f-]{36})/'
    r'download'
)


# ======================================
# 取得毒品 CSV 資源 URL
# ======================================

def get_drug_resource_urls():

    html = fetch_page(
        DRUG_DATASET_PAGE,
        verify_ssl=False
    )

    matches = re.findall(
        DRUG_URL_PATTERN,
        html,
        re.IGNORECASE
    )

    urls = []

    seen = set()

    for dataset_uuid, resource_uuid in matches:

        url = (
            "https://opdadm.moi.gov.tw/"
            "api/v1/no-auth/resource/api/"
            f"dataset/{dataset_uuid}/"
            f"resource/{resource_uuid}/"
            "download"
        )

        if url in seen:
            continue

        seen.add(url)
        urls.append(url)

    print(
        "💊 找到毒品資料資源：",
        len(urls)
    )

    return urls


# ======================================
# 取得所有毒品資料
# ======================================

def fetch_drug_data():

    resource_urls = (
        get_drug_resource_urls()
    )

    all_rows = []

    for index, url in enumerate(
        resource_urls,
        start=1
    ):

        print(
            f"💊 [{index}/{len(resource_urls)}]"
            " 下載毒品資料..."
        )

        try:

            rows = fetch_csv(
                url,
                verify_ssl=False
            )

            all_rows.extend(rows)

            print(
                f"   ✅ {len(rows)} 筆"
            )

        except Exception as error:

            print(
                "   ❌ 下載失敗：",
                error
            )

    print(
        "💊 毒品原始資料總筆數：",
        len(all_rows)
    )

    return all_rows


# ======================================
# 從地址取得縣市
# ======================================

def extract_county(address):

    if not address:
        return None

    address = str(address).strip()

    match = re.match(
        r'^(.+?[縣市])',
        address
    )

    if not match:
        return None

    return match.group(1).strip()


# ======================================
# 從地址取得行政區
# ======================================

def extract_town(address):

    if not address:
        return None

    address = str(address).strip()

    county = extract_county(address)

    if not county:
        return None

    remaining_address = (
        address[len(county):]
        .strip()
    )

    match = re.match(
        r'^([\u4e00-\u9fff]{1,6}'
        r'(?:區|鎮|鄉|市))',
        remaining_address
    )

    if not match:
        return None

    return match.group(1).strip()


# ======================================
# 取得完整行政區名稱
# ======================================

def extract_district_name(address):

    county = extract_county(address)
    town = extract_town(address)

    if not county or not town:
        return None

    district_name = county + town

    return district_name.replace(
        "台",
        "臺"
    )


# ======================================
# 整理單筆毒品資料
# ======================================

def normalize_drug_record(row):

    address = row.get("oc_addr")

    district_name = (
        extract_district_name(address)
    )

    if not district_name:
        return None

    return {
        "no": row.get("no"),
        "type": row.get("type"),
        "date": row.get("oc_dt"),
        "address": row.get("oc_addr"),
        "drug": row.get("kind"),
        "weight_g": row.get("weight_g"),
        "district_name": district_name
    }


# ======================================
# 按行政區統計
# ======================================

def aggregate_drug_by_district(
    records
):

    districts = {}

    invalid_count = 0

    for record in records:

        normalized = (
            normalize_drug_record(record)
        )

        if normalized is None:

            invalid_count += 1

            continue

        district_name = (
            normalized["district_name"]
        )

        if district_name not in districts:

            districts[district_name] = {
                "count": 0,
                "records": []
            }

        districts[
            district_name
        ]["count"] += 1

        districts[
            district_name
        ]["records"].append(
            normalized
        )

    print(
        "💊 成功整理行政區：",
        len(districts)
    )

    print(
        "💊 無法判斷行政區：",
        invalid_count
    )

    return districts


# ======================================
# 對外主要函式
# ======================================

def get_drug_statistics():

    records = fetch_drug_data()

    return aggregate_drug_by_district(
        records
    )


# ======================================
# 單獨測試
# ======================================

if __name__ == "__main__":

    statistics = (
        get_drug_statistics()
    )

    print(
        "💊 有毒品資料的行政區：",
        len(statistics)
    )

    for name, data in list(
        statistics.items()
    )[:5]:

        print(
            name,
            data["count"]
        )