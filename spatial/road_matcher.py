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
    找距離指定點最近的 OSM 道路。

    回傳：
        {
            "roadIndex": 道路在 roads 裡面的 index,
            "road": 道路資料,
            "distance": 距離（公尺）
        }
    """

    point_grid = get_grid_key(
        point_lat,
        point_lng,
        grid_size
    )

    candidate_indexes = set()

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

    if not candidate_indexes:
        return None

    nearest_road_index = None
    nearest_road = None
    nearest_distance = float("inf")

    for road_index in candidate_indexes:

        road = roads[road_index]

        geometry = road.get("geometry")

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
            nearest_road_index = road_index
            nearest_road = road

    if nearest_road is None:
        return None

    if nearest_distance > max_distance:
        return None

    return {
        "roadIndex": nearest_road_index,
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
    將多個點匹配到最近的道路。

    回傳：
        [
            {
                "point": 原始點,
                "roadIndex": 道路 index,
                "road": 道路資料,
                "distance": 距離
            }
        ]
    """

    road_grid = build_road_grid(
        roads,
        grid_size=grid_size
    )

    results = []

    for point in points:

        lat = point.get("lat")
        lng = point.get("lng")

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

        if match is None:
            continue

        results.append({
            "point": point,
            "roadIndex": match["roadIndex"],
            "road": match["road"],
            "distance": match["distance"]
        })

    return results