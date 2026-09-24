import requests
import urllib3


# 關閉政府網站 HTTPS 憑證警告
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_json(url, verify_ssl=False):
    """
    從指定 URL 取得 JSON 資料。

    Parameters
    ----------
    url : str
        JSON API 的網址
    verify_ssl : bool
        是否驗證 HTTPS 憑證

    Returns
    -------
    dict / list
        API 回傳的 JSON 資料
    """

    response = requests.get(
        url,
        headers=DEFAULT_HEADERS,
        timeout=60,
        verify=verify_ssl
    )

    response.raise_for_status()

    return response.json()