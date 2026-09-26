// ==============================
// Google Maps 基本設定
// ==============================

// 輔仁大學淨心堂
const FJU_CENTER = {
    lat: 25.035806,
    lng: 121.433167
};


// ==============================
// 建立 Google Map
// ==============================

function initMap() {

    const map = new google.maps.Map(
        document.getElementById("map"),
        {
            center: FJU_CENTER,
            zoom: 15
        }
    );

    console.log("Google Maps 載入成功");

    // OSM 道路
    loadOSMLayer(map);

    // 安全特徵
    loadSafetyLayer(map);
}