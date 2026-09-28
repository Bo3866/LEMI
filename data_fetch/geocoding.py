import requests

def geocode_address(address: str):
    """
    使用 Photon API 進行地址定位，並補全前端所需的欄位格式
    """
    if not address or not address.strip():
        return None

    url = "https://photon.komoot.io/api/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    params = {
        "q": address,
        "limit": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])

            if features:
                first_match = features[0]
                geometry = first_match.get("geometry", {})
                properties = first_match.get("properties", {})

                # Photon 座標格式為 [經度, 緯度]
                coordinates = geometry.get("coordinates", [0, 0])
                lon = coordinates[0]
                lat = coordinates[1]

                # 提取詳細地址欄位
                name = properties.get("name", "")
                city = properties.get("city", "") or properties.get("state", "")
                country = properties.get("country", "")
                street = properties.get("street", "")
                housenumber = properties.get("housenumber", "")

                formatted_address = f"{country} {city} {street} {housenumber} {name}".strip()
                if not formatted_address:
                    formatted_address = address

                # 【關鍵】完整補齊前端所需的欄位結構，包含 lat, lng 與 details
                return {
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "lat": float(lat),  # 相容前端不同變數命名
                    "lng": float(lon),  # 相容前端不同變數命名
                    "formatted_address": formatted_address,
                    "details": {
                        "country": country,
                        "city": city,
                        "district": properties.get("district", ""),
                        "village": "",
                        "road": street,
                        "house_number": housenumber
                    }
                }
            else:
                print(f"查無結果: {address}")
        else:
            print(f"API 回傳 HTTP 錯誤碼: {response.status_code}")

    except Exception as e:
        print(f"連線發生例外錯誤: {e}")

    return None

# ===== 手動輸入測試區塊 =====
if __name__ == "__main__":
    while True:
        user_input = input("\n請輸入想測試的地點或地址 (輸入 q 離開): ").strip()
        
        if user_input.lower() == 'q':
            print("結束測試。")
            break
            
        if not user_input:
            print("輸入不能為空，請重新輸入！")
            continue

        print(f"正在定位：{user_input} ...")
        res = geocode_address(user_input)
        
        if res:
            print("\n 定位成功！")
            print(f"格式化地址: {res['formatted_address']}")
            print(f"緯度: {res['latitude']}")
            print(f"經度: {res['longitude']}")
        else:
            print("\n 定位失敗，請確認地點名稱或網路連線。")