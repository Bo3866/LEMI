// ==============================
// OSM 道路圖層
// ==============================

const OSM_GEOJSON_URL =
    "/static/test_jingxintang_edges_cut_roads.geojson";


function loadOSMLayer(map) {

    const osmLayer = new google.maps.Data();

    osmLayer.setMap(map);

    osmLayer.loadGeoJson(
        OSM_GEOJSON_URL,
        function(features) {

            console.log(
                "OSM 道路載入成功，共有",
                features.length,
                "條道路"
            );

        }
    );

    return osmLayer;
}