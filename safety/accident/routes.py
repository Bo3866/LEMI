# ==============================
# A1 Flask API
# ==============================

from flask import Blueprint, jsonify

from safety.accident.a1 import (
    get_a1_accidents
)

from safety.accident.spatial_match import (
    match_accidents_to_roads
)

from data_fetch.osm import (
    load_osm_roads
)


# ==============================
# Blueprint
# ==============================

accident_bp = Blueprint(
    "accident",
    __name__
)


# ==============================
# A1 事故 API
# ==============================

@accident_bp.route(
    "/api/accidents-a1"
)
def accidents_a1():

    # --------------------------
    # 取得 A1
    # --------------------------

    accidents = (
        get_a1_accidents()
    )

    # --------------------------
    # 取得 OSM 道路
    # --------------------------

    roads = load_osm_roads()

    # --------------------------
    # 事故 → 道路
    # --------------------------

    matches = (
        match_accidents_to_roads(
            accidents,
            roads,
            max_distance=80
        )
    )

    # --------------------------
    # 整理 API 回傳資料
    # --------------------------

    results = []

    for match in matches:

        accident = match[
            "accident"
        ]

        road = match[
            "road"
        ]

        results.append({

            # ------------------
            # 事故資料
            # ------------------

            "id": accident["id"],

            "lat": accident["lat"],
            "lng": accident["lng"],

            "year": accident["year"],
            "month": accident["month"],

            "date": accident["date"],
            "time": accident["time"],

            "location": accident[
                "location"
            ],

            "weather": accident[
                "weather"
            ],

            "light": accident[
                "light"
            ],

            "roadType": accident[
                "roadType"
            ],

            "speedLimit": accident[
                "speedLimit"
            ],

            # ------------------
            # OSM 道路資料
            # ------------------

            "roadName": road[
                "properties"
            ].get("name"),

            "roadHighway": road[
                "properties"
            ].get("highway"),

            # ------------------
            # 距離
            # ------------------

            "distance": match[
                "distance"
            ]
        })

    return jsonify(
        results
    )