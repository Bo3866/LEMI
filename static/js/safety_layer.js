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
// 毒品行政區圖層
// ======================================

let drugDistrictLayer = null;


// ======================================
// Z-score → 顏色
// ======================================

function getColorByZScore(
    zScore,
    higherIsSafer
) {

    let value = zScore;

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


        const roadStats =
            data.roadStats || [];


        const accidents =
            data.accidents || [];


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


    safetyMarkers.forEach(
        function(marker) {

            marker.setMap(null);
        }
    );


    safetyMarkers = [];


    resetRoadColors();


    console.log(
        "A1 圖層已清除"
    );
}


// ======================================
// 毒品犯罪
//
// API：
// /api/drug-districts
//
// 資料：
// town_boundary.geojson
//
// 每個行政區會有：
// drug_count
// drug_records
// district_name
// ======================================


// ======================================
// 毒品犯罪 → 顏色
// ======================================

function getDrugDistrictColor(
    count
) {

    // 0 件
    if (count === 0) {
        return "#BDBDBD";
    }

    // 1 ~ 100
    if (count <= 100) {
        return "#FFF59D";
    }

    // 101 ~ 500
    if (count <= 500) {
        return "#FFB74D";
    }

    // 501 ~ 1000
    if (count <= 1000) {
        return "#F57C00";
    }

    // > 1000
    return "#D32F2F";
}


// ======================================
// 啟用毒品行政區圖層
// ======================================

async function enableDrugLayer(
    map
) {

    console.log(
        "開始載入毒品犯罪行政區..."
    );


    try {

        const response =
            await fetch(
                "/api/drug-districts"
            );


        if (!response.ok) {

            throw new Error(
                "毒品 API HTTP 錯誤：" +
                response.status
            );
        }


        const geojson =
            await response.json();


        console.log(
            "毒品行政區 GeoJSON 載入完成"
        );


        // ==================================
        // 建立 Google Maps Data 圖層
        // ==================================

        drugDistrictLayer =
            new google.maps.Data();


        // ==================================
        // 行政區樣式
        // ==================================

        drugDistrictLayer.setStyle(
            function(feature) {

                const count =
                    Number(
                        feature.getProperty(
                            "drug_count"
                        )
                    ) || 0;


                const color =
                    getDrugDistrictColor(
                        count
                    );


                return {

                    fillColor: color,

                    fillOpacity: 0.45,

                    strokeColor: "#555555",

                    strokeWeight: 1.5,

                    strokeOpacity: 0.8
                };
            }
        );


        // ==================================
        // 加到地圖
        // ==================================

        drugDistrictLayer.setMap(
            map
        );


        // ==================================
        // 把 GeoJSON 加進 Data layer
        // ==================================

        drugDistrictLayer.addGeoJson(
            geojson
        );


        // ==================================
        // 點擊行政區
        // ==================================

        drugDistrictLayer.addListener(
            "click",
            function(event) {

                const districtName =
                    event.feature.getProperty(
                        "district_name"
                    ) || "未知行政區";


                const count =
                    Number(
                        event.feature.getProperty(
                            "drug_count"
                        )
                    ) || 0;


                const records =
                    event.feature.getProperty(
                        "drug_records"
                    ) || [];


                let content = `
                    <div
                        style="
                            max-width: 350px;
                            max-height: 400px;
                            overflow-y: auto;
                        "
                    >

                        <h3>
                            ${districtName}
                        </h3>

                        <p>
                            💊 毒品案件數量：
                            <b>${count}</b> 件
                        </p>
                `;


                // ==================================
                // 顯示案件
                // ==================================

                if (records.length === 0) {

                    content += `
                        <p>
                            此行政區沒有毒品案件資料。
                        </p>
                    `;

                } else {

                    content += `
                        <hr>
                        <b>案件資料</b>
                    `;


                    records.forEach(
                        function(record) {

                            content += `
                                <hr>

                                <div>

                                    <b>
                                        案件編號：
                                    </b>
                                    ${record.no || "無資料"}
                                    <br>

                                    <b>
                                        日期：
                                    </b>
                                    ${record.date || "無資料"}
                                    <br>

                                    <b>
                                        地址：
                                    </b>
                                    ${record.address || "無資料"}
                                    <br>

                                    <b>
                                        毒品：
                                    </b>
                                    ${record.drug || "無資料"}
                                    <br>

                                    <b>
                                        重量：
                                    </b>
                                    ${record.weight_g || "無資料"} g

                                </div>
                            `;
                        }
                    );
                }


                content += `
                    </div>
                `;


                const infoWindow =
                    new google.maps.InfoWindow({
                        content: content
                    });


                infoWindow.setPosition(
                    event.latLng
                );


                infoWindow.open({
                    map: map
                });
            }
        );


        console.log(
            "毒品犯罪行政區圖層載入完成"
        );

    } catch (error) {

        console.error(
            "毒品犯罪圖層載入失敗：",
            error
        );
    }
}


// ======================================
// 關閉毒品行政區圖層
// ======================================

function disableDrugLayer() {

    console.log(
        "關閉毒品犯罪行政區"
    );


    if (drugDistrictLayer) {

        drugDistrictLayer.setMap(
            null
        );

        drugDistrictLayer = null;
    }


    console.log(
        "毒品犯罪行政區圖層已清除"
    );
}


// ======================================
// 圖層控制
// ======================================

function setupLayerControls(
    map
) {

    // ==================================
    // A1
    // ==================================

    const a1Toggle =
        document.getElementById(
            "a1-toggle"
        );


    if (a1Toggle) {

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

    } else {

        console.warn(
            "找不到 a1-toggle"
        );
    }


    // ==================================
    // 毒品
    // ==================================

    const drugToggle =
        document.getElementById(
            "drug-toggle"
        );


    if (drugToggle) {

        drugToggle.addEventListener(
            "change",
            async function() {

                if (this.checked) {

                    await enableDrugLayer(
                        map
                    );

                } else {

                    disableDrugLayer();
                }
            }
        );

    } else {

        console.warn(
            "找不到 drug-toggle"
        );
    }


    console.log(
        "圖層控制初始化完成"
    );
}