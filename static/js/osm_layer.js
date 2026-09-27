// ==============================
// OSM 道路圖層
// ==============================

const OSM_GEOJSON_URL =
    "/static/test_jingxintang_edges_cut_roads.geojson";


let osmLayer = null;


// roadIndex → Google Maps Data.Feature
const osmFeatures = {};


// ======================================
// 載入 OSM 道路
// ======================================

function loadOSMLayer(map) {

    osmLayer = new google.maps.Data();

    // ----------------------------------
    // 道路樣式
    // ----------------------------------

    osmLayer.setStyle(
        function(feature) {

            const safetyColor =
                feature.getProperty(
                    "safetyColor"
                );

            return {

                strokeColor:
                    safetyColor ||
                    "#1976D2",

                strokeWeight: 4,

                strokeOpacity: 0.9

            };
        }
    );


    osmLayer.setMap(map);


    // ----------------------------------
    // 回傳 Promise
    //
    // 確保 GeoJSON 完成後，
    // 才讓後面的安全特徵開始染色
    // ----------------------------------

    return new Promise(
        function(resolve, reject) {

            osmLayer.loadGeoJson(

                OSM_GEOJSON_URL,

                {},

                function(features) {

                    // ------------------------------
                    // 建立 roadIndex → feature
                    // ------------------------------

                    features.forEach(
                        function(
                            feature,
                            index
                        ) {

                            // 在 Google Maps Feature
                            // 裡面記錄道路 index

                            feature.setProperty(
                                "roadIndex",
                                index
                            );


                            // 建立快速查找表

                            osmFeatures[
                                index
                            ] = feature;
                        }
                    );


                    console.log(
                        "OSM 道路載入成功，共有",
                        features.length,
                        "條道路"
                    );


                    resolve(features);
                }
            );
        }
    );
}


// ======================================
// 取得 OSM layer
// ======================================

function getOSMLayer() {

    return osmLayer;
}


// ======================================
// 幫指定道路染色
// ======================================

function setRoadColor(
    roadIndex,
    color
) {

    const feature =
        osmFeatures[
            roadIndex
        ];


    if (!feature) {

        console.warn(
            "找不到 roadIndex：",
            roadIndex
        );

        return;
    }


    feature.setProperty(
        "safetyColor",
        color
    );
}


// ======================================
// 清除所有安全特徵顏色
// ======================================

function resetRoadColors() {

    Object.values(
        osmFeatures
    ).forEach(
        function(feature) {

            feature.setProperty(
                "safetyColor",
                null
            );
        }
    );
}