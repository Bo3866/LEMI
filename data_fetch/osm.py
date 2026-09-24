# ==============================
# OSM 道路資料
# ==============================

import json


OSM_GEOJSON_PATH = (
    "static/"
    "test_jingxintang_edges_cut_roads.geojson"
)


def load_osm_roads():
    """
    讀取 OSM 道路 GeoJSON。

    回傳：
        list[dict]

    每一個元素都是一條道路的
    GeoJSON Feature。
    """

    with open(
        OSM_GEOJSON_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    roads = data.get(
        "features",
        []
    )

    if not isinstance(
        roads,
        list
    ):
        raise ValueError(
            "OSM GeoJSON 的 features 不是 list"
        )

    return roads


# ==============================
# 測試
# ==============================

if __name__ == "__main__":

    roads = load_osm_roads()

    print(
        "OSM 道路數量：",
        len(roads)
    )