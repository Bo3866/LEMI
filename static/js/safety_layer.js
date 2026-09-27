// ======================================
// 安全特徵圖層
//
// 不管目前是：
// A1、A2、路燈、犯罪、人口......
//
// 都使用同一套 Z-score 染色邏輯。
//
// higher_is_safer：
// true  → 數值越高越安全
// false → 數值越高越危險
//
// 未來這個值會由資料庫提供。
// ======================================


// ======================================
// Z-score → 顏色
// ======================================

function getColorByZScore(
    zScore,
    higherIsSafer
) {

    let value = zScore;


    // ----------------------------------
    // 如果數值越高代表越安全
    //
    // 為了讓「紅色 = 高風險」
    // 所以需要反轉 Z-score
    // ----------------------------------

    if (higherIsSafer) {

        value = -value;
    }


    // ----------------------------------
    // Z > 1
    // ----------------------------------

    if (value > 1) {

        return "#D32F2F";
    }


    // ----------------------------------
    // 0 < Z <= 1
    // ----------------------------------

    if (value > 0) {

        return "#F57C00";
    }


    // ----------------------------------
    // -1 < Z <= 0
    // ----------------------------------

    if (value > -1) {

        return "#FBC02D";
    }


    // ----------------------------------
    // Z <= -1
    // ----------------------------------

    return "#1976D2";
}


// ======================================
// 套用道路 Z-score 顏色
// ======================================

function applyRoadZScoreColors(
    roadStats,
    higherIsSafer
) {

    roadStats.forEach(
        function(stat) {

            const color =
                getColorByZScore(
                    stat.zScore,
                    higherIsSafer
                );


            setRoadColor(
                stat.roadIndex,
                color
            );
        }
    );


    console.log(
        "Z-score 道路染色完成，共",
        roadStats.length,
        "條道路"
    );
}


// ======================================
// 建立安全特徵 Marker
// ======================================

function createSafetyMarker(
    map,
    item
) {

    const marker =
        new google.maps.Marker({

            position: {
                lat: item.lat,
                lng: item.lng
            },

            map: map,

            title:
                item.location ||
                "安全特徵"
        });


    const infoWindow =
        new google.maps.InfoWindow({

            content: `
                <div>
                    <b>安全特徵</b><br>
                    地點：
                    ${item.location || "無資料"}<br>
                    道路：
                    ${item.roadName || "無資料"}<br>
                    距離道路：
                    ${
                        item.distance !== undefined
                            ? item.distance.toFixed(2)
                            : "無資料"
                    } 公尺
                </div>
            `
        });


    marker.addListener(
        "click",
        function() {

            infoWindow.open({
                map: map,
                anchor: marker
            });
        }
    );


    return marker;
}


// ======================================
// 載入安全特徵
// ======================================

async function loadSafetyLayer(
    map
) {

    console.log(
        "開始載入安全特徵..."
    );


    try {

        // ==================================
        // 取得後端資料
        // ==================================

        const response =
            await fetch(
                "/api/accidents-a1"
            );


        if (!response.ok) {

            throw new Error(
                "安全特徵 API HTTP 錯誤：" +
                response.status
            );
        }


        const data =
            await response.json();


        // ==================================
        // 道路統計
        // ==================================

        const roadStats =
            data.roadStats || [];


        // ==================================
        // 安全特徵點
        // ==================================

        const accidents =
            data.accidents || [];


        // ==================================
        // 取得特徵方向
        //
        // 現在暫時由 routes.py 提供
        // 未來改成資料庫提供
        // ==================================

        const higherIsSafer =
            data.higher_is_safer === true;


        console.log(
            "higher_is_safer：",
            higherIsSafer
        );

        console.log(
            "Z-score 範圍：",
            Math.min(
                ...roadStats.map(
                    stat => stat.zScore
                )
            ),
            "~",
            Math.max(
                ...roadStats.map(
                    stat => stat.zScore
                )
            )
        );


        // ==================================
        // Z-score 染色
        // ==================================

        applyRoadZScoreColors(
            roadStats,
            higherIsSafer
        );


        // ==================================
        // 顯示安全特徵點
        // ==================================

        const safetyMarkers = [];


        accidents.forEach(
            function(item) {

                const marker =
                    createSafetyMarker(
                        map,
                        item
                    );


                safetyMarkers.push(
                    marker
                );
            }
        );


        console.log(
            "安全特徵點已顯示，共",
            safetyMarkers.length,
            "個"
        );


    } catch (error) {

        console.error(
            "安全特徵載入失敗：",
            error
        );
    }
}