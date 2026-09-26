// ==============================
// 安全特徵圖層
// ==============================
//
// 目前先使用 A1 交通事故測試。
// 未來可以擴充 A2、路燈、犯罪、人口等安全特徵。
//


// ==============================
// 安全圖層管理
// ==============================

let safetyMarkers = [];


// ==============================
// 載入安全特徵
// ==============================

function loadSafetyLayer(map) {

    console.log("開始載入安全特徵...");

    loadA1Accidents(map);
}


// ==============================
// 載入 A1 事故
// ==============================

async function loadA1Accidents(map) {

    try {

        const response = await fetch(
            "/api/accidents-a1"
        );

        if (!response.ok) {
            throw new Error(
                `A1 API 錯誤：${response.status}`
            );
        }

        const accidents = await response.json();

        console.log(
            "A1 事故資料載入成功，共有",
            accidents.length,
            "筆"
        );


        // ==============================
        // 將事故資料畫到地圖
        // ==============================

        accidents.forEach(
            accident => {

                if (
                    accident.lat == null ||
                    accident.lng == null
                ) {
                    return;
                }

                const marker =
                    new google.maps.Marker({

                        position: {
                            lat: Number(accident.lat),
                            lng: Number(accident.lng)
                        },

                        map: map,

                        title: "A1 交通事故"
                    });


                // ==============================
                // 點擊事故點時顯示資訊
                // ==============================

                const infoWindow =
                    new google.maps.InfoWindow({

                        content: `
                            <div>
                                <strong>A1 交通事故</strong>
                                <br>
                                發生日期：
                                ${accident.date ?? ""}
                                <br>
                                發生時間：
                                ${accident.time ?? ""}
                                <br>
                                發生地點：
                                ${accident.location ?? ""}
                                <br>
                                道路名稱：
                                ${accident.roadName ?? "未知"}
                                <br>
                                距離道路：
                                ${
                                    accident.distance != null
                                        ? Number(
                                            accident.distance
                                          ).toFixed(2)
                                        : "未知"
                                }
                                公尺
                            </div>
                        `
                    });


                marker.addListener(
                    "click",
                    () => {

                        infoWindow.open({
                            anchor: marker,
                            map: map
                        });

                    }
                );


                // ==============================
                // 保存 Marker
                // ==============================

                safetyMarkers.push(marker);

            }
        );


        console.log(
            "A1 事故點已顯示，共",
            safetyMarkers.length,
            "個"
        );


    } catch (error) {

        console.error(
            "載入 A1 事故資料失敗：",
            error
        );

    }
}
