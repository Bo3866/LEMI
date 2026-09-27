const FJU_CENTER = {
    lat: 25.035806,
    lng: 121.433167
};


// ======================================
// Google Maps 初始化
// ======================================

async function initMap() {

    const map =
        new google.maps.Map(
            document.getElementById(
                "map"
            ),
            {
                center: FJU_CENTER,
                zoom: 15
            }
        );


    console.log(
        "Google Maps 載入成功"
    );


    try {

        // ==================================
        // 1. 先載入 OSM
        // ==================================

        await loadOSMLayer(
            map
        );


        console.log(
            "OSM 已完成載入"
        );


        setupLayerControls(map);

    } catch (error) {

        console.error(
            "地圖初始化失敗：",
            error
        );
    }
}