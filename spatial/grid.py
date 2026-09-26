# ==============================
# 空間 Grid
# ==============================

GRID_SIZE = 0.001


def get_grid_key(
    lat,
    lng,
    grid_size=GRID_SIZE
):
    """
    將經緯度轉換成 Grid 編號。
    """

    return (
        int(lat / grid_size),
        int(lng / grid_size)
    )


def get_neighbor_grid_keys(
    grid_key,
    radius=1
):
    """
    取得指定 Grid 周圍的 Grid。

    radius=1：
        會取得 3 × 3 = 9 個 Grid。
    """

    grid_lat, grid_lng = grid_key

    neighbors = []

    for lat_offset in range(
        -radius,
        radius + 1
    ):
        for lng_offset in range(
            -radius,
            radius + 1
        ):
            neighbors.append(
                (
                    grid_lat + lat_offset,
                    grid_lng + lng_offset
                )
            )

    return neighbors


def get_road_bounds(road):
    """
    取得道路 GeoJSON 的經緯度範圍。

    回傳：
        min_lat,
        max_lat,
        min_lng,
        max_lng
    """

    geometry = road.get(
        "geometry"
    )

    if not geometry:
        return None

    coordinates = geometry.get(
        "coordinates",
        []
    )

    if not coordinates:
        return None

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


def build_road_grid(
    roads,
    grid_size=GRID_SIZE
):
    """
    建立道路 Grid 索引。

    回傳：

    {
        (grid_lat, grid_lng): [
            road_index,
            road_index,
            ...
        ]
    }
    """

    road_grid = {}

    for road_index, road in enumerate(roads):

        bounds = get_road_bounds(
            road
        )

        if bounds is None:
            continue

        min_lat, max_lat, min_lng, max_lng = bounds

        min_grid_lat = int(
            min_lat / grid_size
        )

        max_grid_lat = int(
            max_lat / grid_size
        )

        min_grid_lng = int(
            min_lng / grid_size
        )

        max_grid_lng = int(
            max_lng / grid_size
        )

        for grid_lat in range(
            min_grid_lat,
            max_grid_lat + 1
        ):
            for grid_lng in range(
                min_grid_lng,
                max_grid_lng + 1
            ):

                key = (
                    grid_lat,
                    grid_lng
                )

                if key not in road_grid:
                    road_grid[key] = []

                road_grid[key].append(
                    road_index
                )

    return road_grid