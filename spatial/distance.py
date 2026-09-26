# ==============================
# 空間距離計算
# ==============================

import math


# 地球半徑（公尺）
EARTH_RADIUS = 6371000


def latlng_to_xy(lat, lng, origin_lat):
    """
    將經緯度轉換成局部平面座標（公尺）。

    用於計算兩個地理座標之間的距離。
    """

    lat_rad = math.radians(lat)
    origin_lat_rad = math.radians(origin_lat)

    x = (
        math.radians(lng)
        * EARTH_RADIUS
        * math.cos(origin_lat_rad)
    )

    y = (
        math.radians(lat)
        * EARTH_RADIUS
    )

    return x, y


def point_to_segment_distance(
    point_lat,
    point_lng,
    start_lat,
    start_lng,
    end_lat,
    end_lng
):
    """
    計算「一個點」到「一條線段」的最短距離。

    回傳：
        距離（公尺）
    """

    # 使用線段起點當作局部座標原點
    origin_lat = start_lat

    px, py = latlng_to_xy(
        point_lat,
        point_lng,
        origin_lat
    )

    ax, ay = latlng_to_xy(
        start_lat,
        start_lng,
        origin_lat
    )

    bx, by = latlng_to_xy(
        end_lat,
        end_lng,
        origin_lat
    )

    # 向量 AB
    ab_x = bx - ax
    ab_y = by - ay

    # 向量 AP
    ap_x = px - ax
    ap_y = py - ay

    # AB 長度平方
    ab_length_squared = (
        ab_x * ab_x
        + ab_y * ab_y
    )

    # 如果線段長度為 0
    if ab_length_squared == 0:
        return math.sqrt(
            ap_x * ap_x
            + ap_y * ap_y
        )

    # 點投影到線段上的位置
    t = (
        ap_x * ab_x
        + ap_y * ab_y
    ) / ab_length_squared

    # 限制在線段範圍內
    t = max(0, min(1, t))

    # 線段上最接近的點
    closest_x = ax + t * ab_x
    closest_y = ay + t * ab_y

    # 計算距離
    dx = px - closest_x
    dy = py - closest_y

    distance = math.sqrt(
        dx * dx
        + dy * dy
    )

    return distance


def point_to_linestring_distance(
    point_lat,
    point_lng,
    coordinates
):
    """
    計算一個點到整條 LineString 的最短距離。

    coordinates 格式：

    [
        [lng, lat],
        [lng, lat],
        ...
    ]

    回傳：
        最短距離（公尺）
    """

    if not coordinates:
        return float("inf")

    if len(coordinates) == 1:
        lat = coordinates[0][1]
        lng = coordinates[0][0]

        return point_to_segment_distance(
            point_lat,
            point_lng,
            lat,
            lng,
            lat,
            lng
        )

    min_distance = float("inf")

    for i in range(len(coordinates) - 1):

        start_lng, start_lat = coordinates[i]
        end_lng, end_lat = coordinates[i + 1]

        distance = point_to_segment_distance(
            point_lat,
            point_lng,
            start_lat,
            start_lng,
            end_lat,
            end_lng
        )

        if distance < min_distance:
            min_distance = distance

    return min_distance