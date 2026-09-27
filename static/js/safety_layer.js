// ======================================
// 安全特徵圖層
//
// 目前：先以 A1 交通事故為例
//
// 未來：
// A1、A2、路燈、犯罪、人口......
// 都可以共用這套 Z-score 染色邏輯。
//
// higher_is_safer：
// true  → 數值越高越安全
// false → 數值越高越危險
//
// 未來這個值可以由資料庫提供。
// ======================================


// ======================================
// 目前啟用中的安全特徵 Marker
// ======================================

let safetyMarkers = [];


// ======================================
// Z-score → 顏色
// ======================================

function getColorByZScore(
    zScore,
    higherIsSafer
) {

    let value = zScore;


    // 如果數值越高代表越安全
    // 為了讓「紅色 = 高風險」
    // 所以反轉 Z-score

    if (higherIsSafer) {

        value = -value;
    }


    // Z > 1
    if (value > 1) {

        return "#D32F2F";
    }


    // 0 < Z <= 1
    if (value > 0) {

        return "#F57C00";
    }


    // -1 < Z <= 0
    if (value > -1) {

        return "#FBC02D";
    }


    // Z <= -1
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
// 啟用 A1
//
// 目前先寫 A1。
// 未來資料庫建立後，
// 可以把 API、名稱、higher_is_safer
// 改成由資料庫提供。
// ======================================

async function enableA1Layer(
    map
) {

    console.log(
        "開始載入 A1 交通事故..."
    );


    try {

        const response =
            await fetch(
                "/api/accidents-a1"
            );


        if (!response.ok) {

            throw new Error(
                "A1 API HTTP 錯誤：" +
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
        // A1 事故點
        // ==================================

        const accidents =
            data.accidents || [];


        // ==================================
        // 安全特徵方向
        // ==================================

        const higherIsSafer =
            data.higher_is_safer === true;


        console.log(
            "A1 higher_is_safer：",
            higherIsSafer
        );


        console.log(
            "A1 道路資料：",
            roadStats.length
        );


        console.log(
            "A1 事故點：",
            accidents.length
        );


        // ==================================
        // Z-score 染色
        // ==================================

        applyRoadZScoreColors(
            roadStats,
            higherIsSafer
        );


        // ==================================
        // 顯示事故點
        // ==================================

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
            "A1 載入完成"
        );


    } catch (error) {

        console.error(
            "A1 載入失敗：",
            error
        );
    }
}


// ======================================
// 關閉 A1
// ======================================

function disableA1Layer() {

    console.log(
        "關閉 A1 交通事故"
    );


    // ==================================
    // 清除 A1 Marker
    // ==================================

    safetyMarkers.forEach(
        function(marker) {

            marker.setMap(null);
        }
    );


    safetyMarkers = [];


    // ==================================
    // 恢復 OSM 原本顏色
    // ==================================

    resetRoadColors();


    console.log(
        "A1 圖層已清除"
    );
}


// ======================================
// 圖層控制
// ======================================

function setupLayerControls(
    map
) {

    const a1Toggle =
        document.getElementById(
            "a1-toggle"
        );


    if (!a1Toggle) {

        console.error(
            "找不到 a1-toggle"
        );

        return;
    }


    a1Toggle.addEventListener(
        "change",
        async function() {

            if (this.checked) {

                await enableA1Layer(
                    map
                );

            } else {

                disableA1Layer();
            }
        }
    );


    console.log(
        "圖層控制初始化完成"
    );
}