from flask import (
    Blueprint,
    jsonify
)
import json


# ======================================
# A1
# ======================================

from safety.accident.a1 import (
    get_a1_accidents
)


# ======================================
# A2
# ======================================
'''
from safety.accident.a2 import (
    get_a2_accidents
)
'''

# ======================================
# 毒品
# ======================================

from safety.crime.drug import (
    get_drug_statistics
)


# ======================================
# OSM
# ======================================

from data_fetch.osm import (
    load_osm_roads
)


# ======================================
# 空間道路匹配
# ======================================

from spatial.road_matcher import (
    match_points_to_roads
)


# ======================================
# Safety Blueprint
# ======================================

safety_bp = Blueprint(
    "safety",
    __name__
)


MAX_DISTANCE = 80


# ======================================
# Z-score
# ======================================

def calculate_z_scores(values):

    if not values:
        return []

    mean = sum(values) / len(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    standard_deviation = variance ** 0.5

    if standard_deviation == 0:
        return [
            0
            for _ in values
        ]

    return [
        (value - mean)
        / standard_deviation
        for value in values
    ]


# ======================================
# 道路統計
# ======================================

def build_road_statistics(
    roads,
    matched_points
):

    point_counts = [
        0
        for _ in roads
    ]

    for match in matched_points:

        road_index = (
            match["roadIndex"]
        )

        point_counts[
            road_index
        ] += 1

    z_scores = calculate_z_scores(
        point_counts
    )

    road_stats = []

    for road_index, road in enumerate(
        roads
    ):

        properties = road.get(
            "properties",
            {}
        )

        road_stats.append({

            "roadIndex": road_index,

            "value": point_counts[
                road_index
            ],

            "zScore": z_scores[
                road_index
            ],

            "roadName": properties.get(
                "name"
            ),

            "osmid": properties.get(
                "osmid"
            ),

            "highway": properties.get(
                "highway"
            )

        })

    return road_stats


# ======================================
# A1
# ======================================

@safety_bp.route(
    "/api/accidents-a1"
)
def accidents_a1():

    accidents = get_a1_accidents()

    print(
        "A1 事故資料：",
        len(accidents),
        "筆"
    )

    roads = load_osm_roads()

    print(
        "OSM 道路：",
        len(roads),
        "條"
    )

    matched = match_points_to_roads(
        points=accidents,
        roads=roads,
        max_distance=MAX_DISTANCE
    )

    print(
        "A1 成功匹配道路：",
        len(matched),
        "筆"
    )

    road_stats = build_road_statistics(
        roads,
        matched
    )

    accident_results = []

    for item in matched:

        point = item["point"]
        road = item["road"]

        road_index = item[
            "roadIndex"
        ]

        properties = road.get(
            "properties",
            {}
        )

        accident_results.append({

            "id": point.get("id"),

            "year": point.get("year"),

            "month": point.get("month"),

            "date": point.get("date"),

            "time": point.get("time"),

            "lat": point.get("lat"),

            "lng": point.get("lng"),

            "location": point.get(
                "location"
            ),

            "weather": point.get(
                "weather"
            ),

            "light": point.get(
                "light"
            ),

            "roadType": point.get(
                "roadType"
            ),

            "speedLimit": point.get(
                "speedLimit"
            ),

            "accidentType": point.get(
                "accidentType"
            ),

            "accidentSubType": point.get(
                "accidentSubType"
            ),

            "roadIndex": road_index,

            "roadName": properties.get(
                "name"
            ),

            "roadHighway": properties.get(
                "highway"
            ),

            "osmid": properties.get(
                "osmid"
            ),

            "distance": item[
                "distance"
            ]

        })

    return jsonify({

        "higher_is_safer": False,

        "accidents": accident_results,

        "roadStats": road_stats

    })


# ======================================
# A2
# ======================================

@safety_bp.route(
    "/api/accidents-a2"
)
def accidents_a2():

    accidents = get_a2_accidents()

    print(
        "A2 事故資料：",
        len(accidents),
        "筆"
    )

    roads = load_osm_roads()

    print(
        "OSM 道路：",
        len(roads),
        "條"
    )

    matched = match_points_to_roads(
        points=accidents,
        roads=roads,
        max_distance=MAX_DISTANCE
    )

    print(
        "A2 成功匹配道路：",
        len(matched),
        "筆"
    )

    road_stats = build_road_statistics(
        roads,
        matched
    )

    accident_results = []

    for item in matched:

        point = item["point"]
        road = item["road"]

        road_index = item[
            "roadIndex"
        ]

        properties = road.get(
            "properties",
            {}
        )

        accident_results.append({

            "id": point.get("id"),

            "year": point.get("year"),

            "month": point.get("month"),

            "date": point.get("date"),

            "time": point.get("time"),

            "lat": point.get("lat"),

            "lng": point.get("lng"),

            "location": point.get(
                "location"
            ),

            "weather": point.get(
                "weather"
            ),

            "light": point.get(
                "light"
            ),

            "roadType": point.get(
                "roadType"
            ),

            "speedLimit": point.get(
                "speedLimit"
            ),

            "accidentType": point.get(
                "accidentType"
            ),

            "accidentSubType": point.get(
                "accidentSubType"
            ),

            "roadIndex": road_index,

            "roadName": properties.get(
                "name"
            ),

            "roadHighway": properties.get(
                "highway"
            ),

            "osmid": properties.get(
                "osmid"
            ),

            "distance": item[
                "distance"
            ]

        })

    return jsonify({

        "higher_is_safer": False,

        "accidents": accident_results,

        "roadStats": road_stats

    })


# ======================================
# 毒品行政區
# ======================================

TOWN_BOUNDARY_GEOJSON_PATH = (
    "static/town_boundary.geojson"
)


def load_town_boundary():

    with open(
        TOWN_BOUNDARY_GEOJSON_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def build_drug_geojson():

    # ------------------------------
    # ① 取得毒品統計
    # ------------------------------

    district_statistics = (
        get_drug_statistics()
    )

    print(
        "💊 毒品行政區統計：",
        len(district_statistics)
    )


    # ------------------------------
    # ② 讀取行政區 Polygon
    # ------------------------------

    boundary_data = (
        load_town_boundary()
    )

    matched_count = 0

    boundary_names = []

    for feature in boundary_data.get(
        "features",
        []
    ):

        properties = feature.get(
            "properties",
            {}
        )

        county_name = (
            properties.get(
                "COUNTYNAME"
            )
            or properties.get(
                "COUNTY_NAME"
            )
        )

        town_name = (
            properties.get(
                "TOWNNAME"
            )
            or properties.get(
                "TOWN_NAME"
            )
        )

        district_name = (
            (county_name or "")
            +
            (town_name or "")
        )

        boundary_names.append(
            district_name
        )

    print(
        "🗺️ 隸屬區 GeoJSON 行政區數量：",
        len(boundary_names)
    )

    print(
        "🗺️ 前 20 個行政區："
    )

    for name in boundary_names[:20]:
        print(
            "   -",
            name
        )

    # 用來記錄「成功配對」的行政區名稱
    matched_names = set()


    # ------------------------------
    # ③ 合併毒品資料
    # ------------------------------

    for feature in boundary_data.get(
        "features",
        []
    ):

        properties = feature.setdefault(
            "properties",
            {}
        )


        county_name = (
            properties.get(
                "COUNTYNAME"
            )
            or properties.get(
                "COUNTY_NAME"
            )
        )


        town_name = (
            properties.get(
                "TOWNNAME"
            )
            or properties.get(
                "TOWN_NAME"
            )
        )


        district_name = (
            (county_name or "")
            +
            (town_name or "")
        )


        drug_info = (
            district_statistics.get(
                district_name
            )
        )


        if drug_info:

            properties[
                "drug_count"
            ] = drug_info["count"]

            properties[
                "drug_records"
            ] = drug_info["records"]

            matched_count += 1

            # 記錄成功配對的名稱
            matched_names.add(
                district_name
            )

        else:

            properties[
                "drug_count"
            ] = 0

            properties[
                "drug_records"
            ] = []


        properties[
            "district_name"
        ] = district_name


    # ------------------------------
    # ④ 找出沒有配對成功的行政區
    # ------------------------------

    unmatched_names = (
        set(district_statistics.keys())
        - matched_names
    )


    print(
        "💊 成功配對行政區：",
        matched_count
    )

    print(
        "💊 找不到對應行政區：",
        len(unmatched_names)
    )

    print(
        "💊 找不到對應的行政區名稱："
    )

    for name in sorted(
        unmatched_names
    ):
        print(
            "   -",
            name
        )


    # ------------------------------
    # ⑤ 回傳完整 GeoJSON
    # ------------------------------

    return boundary_data

# ======================================
# 毒品行政區 API
# ======================================

@safety_bp.route(
    "/api/drug-districts"
)
def drug_districts():

    try:

        print(
            "================================"
        )

        print(
            "💊 開始取得毒品行政區資料"
        )

        print(
            "================================"
        )

        data = build_drug_geojson()

        return jsonify(data)

    except Exception as error:

        print(
            "❌ 毒品 API 發生錯誤：",
            error
        )

        return jsonify({
            "error": str(error)
        }), 500