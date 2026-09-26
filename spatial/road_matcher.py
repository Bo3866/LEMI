# ==============================
# 通用道路配對
# ==============================

from spatial.distance import (
    point_to_linestring_distance
)

from spatial.grid import (
    GRID_SIZE,
    get_grid_key,
    get_neighbor_grid_keys,
    build_road_grid
)


def find_nearest_road(
    point_lat,
    point_lng,
    roads,
    road_grid,
    max_distance=80,
    grid_size=GRID_SIZE
):
    """
    找出一個點附近最近的道路。

    參數：
        point_lat
            點的緯度

        point_lng
            點的經度

        roads
            OSM 道路 GeoJSON features

        road_grid
            已建立的道路 Grid

        max_distance
            最大允許距離（公尺）

        grid_size
            Grid 大小

    回傳：

    {
        "road": 道路資料,
        "distance": 距離
    }

    如果找不到：
        None
    """

    point_grid = get_grid_key(
        point_lat,
        point_lng,
        grid_size
    )

    candidate_indexes = set()

    # 先找附近的 Grid
    neighbor_grids = get_neighbor_grid_keys(
        point_grid,
        radius=1
    )

    for grid_key in neighbor_grids:

        road_indexes = road_grid.get(
            grid_key,
            []
        )

        candidate_indexes.update(
            road_indexes
        )

    # 沒有候選道路
    if not candidate_indexes:
        return None

    nearest_road = None
    nearest_distance = float("inf")

    # 只計算候選道路
    for road_index in candidate_indexes:

        road = roads[road_index]

        geometry = road.get(
            "geometry"
        )

        if not geometry:
            continue

        coordinates = geometry.get(
            "coordinates",
            []
        )

        if not coordinates:
            continue

        distance = point_to_linestring_distance(
            point_lat,
            point_lng,
            coordinates
        )

        if distance < nearest_distance:

            nearest_distance = distance
            nearest_road = road

    # 超過最大距離
    if (
        nearest_road is None
        or nearest_distance > max_distance
    ):
        return None

    return {
        "road": nearest_road,
        "distance": nearest_distance
    }


def match_points_to_roads(
    points,
    roads,
    max_distance=80,
    grid_size=GRID_SIZE
):
    """
    將多個點資料配對到 OSM 道路。

    points 不限定一定是事故資料。

    每個 point 只需要有：

        lat
        lng

    回傳：

    [
        {
            "point": 原始點資料,
            "road": 道路資料,
            "distance": 距離
        },
        ...
    ]
    """

    # 建立道路 Grid
    road_grid = build_road_grid(
        roads,
        grid_size=grid_size
    )

    results = []

    for point in points:

        lat = point.get("lat")
        lng = point.get("lng")

        # 沒有座標就跳過
        if lat is None or lng is None:
            continue

        match = find_nearest_road(
            point_lat=lat,
            point_lng=lng,
            roads=roads,
            road_grid=road_grid,
            max_distance=max_distance,
            grid_size=grid_size
        )

        # 找不到道路就跳過
        if match is None:
            continue

        results.append({
            "point": point,
            "road": match["road"],
            "distance": match["distance"]
        })

    return results