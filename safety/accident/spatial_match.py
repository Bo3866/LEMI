# ==============================
# 事故點與道路空間比對
# Grid 加速版
# ==============================

import math


# ==============================
# 基本設定
# ==============================

EARTH_RADIUS = 6371000

# Grid 大小
# 0.001 度大約是 100 公尺左右
GRID_SIZE = 0.001


# ==============================
# 經緯度 → 平面座標
# ==============================

def latlng_to_xy(
    lat,
    lng,
    reference_lat
):
    """
    將經緯度轉成適合計算距離的平面座標。

    回傳：
        x, y
    """

    lat_rad = math.radians(
        reference_lat
    )

    x = (
        math.radians(lng)
        * EARTH_RADIUS
        * math.cos(lat_rad)
    )

    y = (
        math.radians(lat)
        * EARTH_RADIUS
    )

    return x, y


# ==============================
# 點 → 線段距離
# ==============================

def point_to_segment_distance(
    point_lat,
    point_lng,
    start_lat,
    start_lng,
    end_lat,
    end_lng
):
    """
    計算一個點到一條線段的最短距離。

    單位：公尺
    """

    reference_lat = point_lat

    px, py = latlng_to_xy(
        point_lat,
        point_lng,
        reference_lat
    )

    ax, ay = latlng_to_xy(
        start_lat,
        start_lng,
        reference_lat
    )

    bx, by = latlng_to_xy(
        end_lat,
        end_lng,
        reference_lat
    )

    dx = bx - ax
    dy = by - ay

    # 如果線段起點與終點相同
    if dx == 0 and dy == 0:

        return math.sqrt(
            (px - ax) ** 2 +
            (py - ay) ** 2
        )

    # 計算投影位置
    t = (
        (px - ax) * dx +
        (py - ay) * dy
    ) / (
        dx * dx +
        dy * dy
    )

    # 限制在 0～1
    t = max(
        0,
        min(1, t)
    )

    # 找出線段上距離最近的點
    closest_x = ax + t * dx
    closest_y = ay + t * dy

    distance = math.sqrt(
        (px - closest_x) ** 2 +
        (py - closest_y) ** 2
    )

    return distance


# ==============================
# 點 → 整條道路距離
# ==============================

def point_to_linestring_distance(
    point,
    road_feature
):
    """
    計算事故點到整條 OSM 道路的最短距離。

    point：
        事故資料

    road_feature：
        GeoJSON 道路 Feature

    回傳：
        最短距離（公尺）
    """

    lat = point["lat"]
    lng = point["lng"]

    coordinates = (
        road_feature["geometry"]["coordinates"]
    )

    min_distance = float("inf")

    # 一段一段線段計算
    for i in range(
        len(coordinates) - 1
    ):

        start_lng, start_lat = (
            coordinates[i]
        )

        end_lng, end_lat = (
            coordinates[i + 1]
        )

        distance = point_to_segment_distance(
            lat,
            lng,
            start_lat,
            start_lng,
            end_lat,
            end_lng
        )

        if distance < min_distance:
            min_distance = distance

    return min_distance


# ============================================================
# Grid
# ============================================================

def get_grid_key(
    lat,
    lng
):
    """
    根據經緯度取得 Grid 編號。

    例如：

        (25.035, 121.433)
            ↓
        (25035, 121433)

    """

    row = math.floor(
        lat / GRID_SIZE
    )

    col = math.floor(
        lng / GRID_SIZE
    )

    return row, col


# ==============================
# 取得附近 Grid
# ==============================

def get_neighbor_grid_keys(
    lat,
    lng,
    radius=1
):
    """
    取得事故所在 Grid 周圍的 Grid。

    radius=1：

        ┌─────┬─────┬─────┐
        │ -1  │  0  │ +1  │
        ├─────┼─────┼─────┤
        │ -1  │事故 │ +1  │
        ├─────┼─────┼─────┤
        │ -1  │  0  │ +1  │
        └─────┴─────┴─────┘

    總共 9 格。
    """

    row, col = get_grid_key(
        lat,
        lng
    )

    keys = []

    for row_offset in range(
        -radius,
        radius + 1
    ):

        for col_offset in range(
            -radius,
            radius + 1
        ):

            keys.append(
                (
                    row + row_offset,
                    col + col_offset
                )
            )

    return keys


# ============================================================
# 道路 Grid
# ============================================================

def get_road_bounds(
    road_feature
):
    """
    取得道路的經緯度範圍。

    回傳：

        min_lat
        max_lat
        min_lng
        max_lng
    """

    coordinates = (
        road_feature["geometry"]["coordinates"]
    )

    lats = []
    lngs = []

    for lng, lat in coordinates:

        lats.append(lat)
        lngs.append(lng)

    return (
        min(lats),
        max(lats),
        min(lngs),
        max(lngs)
    )


# ==============================
# 建立道路 Grid
# ==============================

def build_road_grid(
    roads
):
    """
    將 OSM 道路放進 Grid。

    一條道路如果跨越多個 Grid，
    就會被放進多個 Grid。

    回傳：

        {
            (grid_row, grid_col):
                [道路 index, 道路 index, ...]
        }
    """

    grid = {}

    for road_index, road in enumerate(
        roads
    ):

        (
            min_lat,
            max_lat,
            min_lng,
            max_lng
        ) = get_road_bounds(
            road
        )

        min_row, min_col = get_grid_key(
            min_lat,
            min_lng
        )

        max_row, max_col = get_grid_key(
            max_lat,
            max_lng
        )

        # 道路可能跨越很多 Grid
        for row in range(
            min_row,
            max_row + 1
        ):

            for col in range(
                min_col,
                max_col + 1
            ):

                key = (
                    row,
                    col
                )

                if key not in grid:
                    grid[key] = []

                grid[key].append(
                    road_index
                )

    return grid


# ============================================================
# 找最近道路
# ============================================================

def find_nearest_road(
    accident,
    roads,
    road_grid=None,
    max_distance=None
):
    """
    找出距離事故點最近的道路。

    如果有 road_grid：
        只搜尋附近 Grid 的道路。

    如果沒有 road_grid：
        搜尋全部道路。

    回傳：

        {
            "road": 道路 Feature,
            "distance": 最短距離
        }

    如果沒有道路：
        None
    """

    # ========================================================
    # 決定候選道路
    # ========================================================

    if road_grid is None:

        # 沒有 Grid
        # → 搜尋全部道路

        candidate_indices = range(
            len(roads)
        )

    else:

        # 有 Grid
        # → 只搜尋附近 Grid

        candidate_indices = set()

        neighbor_keys = (
            get_neighbor_grid_keys(
                accident["lat"],
                accident["lng"],
                radius=1
            )
        )

        for key in neighbor_keys:

            road_indices = (
                road_grid.get(
                    key,
                    []
                )
            )

            candidate_indices.update(
                road_indices
            )

    # ========================================================
    # 計算最近道路
    # ========================================================

    nearest_road = None

    nearest_distance = float(
        "inf"
    )

    for road_index in candidate_indices:

        road = roads[
            road_index
        ]

        distance = (
            point_to_linestring_distance(
                accident,
                road
            )
        )

        if distance < nearest_distance:

            nearest_distance = distance

            nearest_road = road

    # 沒有找到道路
    if nearest_road is None:
        return None

    # ========================================================
    # 最大距離限制
    # ========================================================

    if (
        max_distance is not None
        and nearest_distance > max_distance
    ):

        return None

    return {
        "road": nearest_road,
        "distance": nearest_distance
    }


# ============================================================
# 事故 → 道路
# ============================================================

def match_accidents_to_roads(
    accidents,
    roads,
    max_distance=80
):
    """
    將事故點配對到道路。

    使用 Grid 加速搜尋。

    流程：

        事故
          ↓
        找事故所在 Grid
          ↓
        找附近 Grid
          ↓
        取得附近道路
          ↓
        計算實際距離
          ↓
        找最近道路
          ↓
        檢查最大距離
          ↓
        回傳配對結果
    """

    # ========================================================
    # 建立道路 Grid
    # ========================================================

    road_grid = build_road_grid(
        roads
    )

    print(
        "道路 Grid 建立完成，共有",
        len(road_grid),
        "個 Grid"
    )

    # ========================================================
    # 開始配對
    # ========================================================

    results = []

    for accident in accidents:

        match = find_nearest_road(
            accident,
            roads,
            road_grid=road_grid,
            max_distance=max_distance
        )

        if match is None:
            continue

        results.append({
            "accident": accident,

            "road": match[
                "road"
            ],

            "distance": match[
                "distance"
            ]
        })

    return results


# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":

    from safety.accident.a1 import (
        get_a1_accidents
    )

    from data_fetch.osm import (
        load_osm_roads
    )

    # ========================================================
    # 取得 A1 事故
    # ========================================================

    accidents = (
        get_a1_accidents()
    )

    # ========================================================
    # 取得 OSM 道路
    # ========================================================

    roads = load_osm_roads()

    # ========================================================
    # 顯示基本資料
    # ========================================================

    print(
        "A1 事故數量：",
        len(accidents)
    )

    print(
        "OSM 道路數量：",
        len(roads)
    )

    # ========================================================
    # Grid 配對
    # ========================================================

    matches = (
        match_accidents_to_roads(
            accidents,
            roads,
            max_distance=80
        )
    )

    print(
        "成功配對的事故數量：",
        len(matches)
    )

    # ========================================================
    # 顯示第一筆
    # ========================================================

    if matches:

        print(
            "\n第一筆配對結果："
        )

        print(
            matches[0]
        )

        print(
            "\n第一筆事故距離道路："
        )

        print(
            matches[0]["distance"],
            "公尺"
        )