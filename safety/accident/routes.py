# ======================================
# A1 安全特徵設定
# ======================================

HIGHER_IS_SAFER = False

# ==============================
# 事故 Flask API
# ==============================

from flask import Blueprint, jsonify

from data_fetch.osm import (
    load_osm_roads
)

from safety.accident.a1 import (
    get_a1_accidents
)

from spatial.road_matcher import (
    match_points_to_roads
)


accident_bp = Blueprint(
    "accident",
    __name__
)


MAX_DISTANCE = 80


def calculate_z_scores(values):
    """
    計算 Z-score。

    Z = (X - 平均值) / 標準差

    這裡使用母體標準差，
    因為我們要分析的是研究範圍內「全部道路」。
    """

    if not values:
        return []

    mean = sum(values) / len(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    standard_deviation = variance ** 0.5

    # 如果所有道路數值都一樣
    if standard_deviation == 0:

        return [
            0
            for _ in values
        ]

    return [
        (value - mean) / standard_deviation
        for value in values
    ]


def build_road_statistics(
    roads,
    matched_accidents
):
    """
    統計每條道路的事故數量，
    並計算 Z-score。
    """

    # --------------------------------
    # 1. 建立每條道路的事故計數
    # --------------------------------

    accident_counts = [
        0
        for _ in roads
    ]

    for match in matched_accidents:

        road_index = match["roadIndex"]

        accident_counts[
            road_index
        ] += 1

    # --------------------------------
    # 2. 計算 Z-score
    # --------------------------------

    z_scores = calculate_z_scores(
        accident_counts
    )

    # --------------------------------
    # 3. 建立道路統計資料
    # --------------------------------

    road_stats = []

    for road_index, road in enumerate(roads):

        properties = road.get(
            "properties",
            {}
        )

        road_stats.append({
            "roadIndex": road_index,

            "value": accident_counts[
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


@accident_bp.route(
    "/api/accidents-a1"
)
def accidents_a1():

    # ==================================
    # 1. 讀取 A1 事故資料
    # ==================================

    accidents = get_a1_accidents()

    print(
        "A1 事故資料：",
        len(accidents),
        "筆"
    )

    # ==================================
    # 2. 讀取 OSM 道路
    # ==================================

    roads = load_osm_roads()

    print(
        "OSM 道路：",
        len(roads),
        "條"
    )

    # ==================================
    # 3. 將事故點匹配到道路
    # ==================================

    matched = match_points_to_roads(
        points=accidents,
        roads=roads,
        max_distance=MAX_DISTANCE
    )

    print(
        "成功匹配道路：",
        len(matched),
        "筆"
    )

    # ==================================
    # 4. 建立道路統計 + Z-score
    # ==================================

    road_stats = build_road_statistics(
        roads,
        matched
    )

    print("========== 道路事故數量 ==========")

    for stat in road_stats:
        if stat["value"] > 0:
            print(
                "roadIndex:",
                stat["roadIndex"],
                "| 事故數:",
                stat["value"],
                "| Z-score:",
                stat["zScore"],
                "| 道路:",
                stat["roadName"]
            )

    print("================================")

    roads_with_accidents = [
        stat
        for stat in road_stats
        if stat["value"] > 0
    ]

    print(
        "有事故的道路數量：",
        len(roads_with_accidents)
    )

    print(
        "最高事故數：",
        max(
            stat["value"]
            for stat in road_stats
        )
    )

    print("========== Z-score 檢查 ==========")

    for stat in road_stats:

        if stat["value"] > 0:

            print(
                "roadIndex:",
                stat["roadIndex"],
                "事故數:",
                stat["value"],
                "Z-score:",
                stat["zScore"],
                "道路:",
                stat["roadName"]
            )

    print("===================================")

    # ==================================
    # 5. 整理事故資料給前端
    # ==================================

    accident_results = []

    for item in matched:

        point = item["point"]
        road = item["road"]
        road_index = item["roadIndex"]

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

            # --------------------------
            # 匹配到的道路
            # --------------------------

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

    # ==================================
    # 6. 回傳
    # ==================================

    return jsonify({

        "higher_is_safer": 
            HIGHER_IS_SAFER,

        "accidents":
            accident_results,

        "roadStats":
            road_stats

    })