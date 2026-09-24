import io
import json
import re
import zipfile

import requests
import urllib3


urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_page(url, verify_ssl=False):
    """
    取得網頁 HTML。
    """

    response = requests.get(
        url,
        headers=DEFAULT_HEADERS,
        timeout=60,
        verify=verify_ssl
    )

    response.raise_for_status()

    return response.text


def download_file(url, verify_ssl=False):
    """
    下載檔案並回傳 bytes。
    """

    response = requests.get(
        url,
        headers=DEFAULT_HEADERS,
        timeout=120,
        verify=verify_ssl
    )

    response.raise_for_status()

    return response.content


def find_zip_urls(
    page_url,
    filename_pattern,
    download_url_pattern,
    verify_ssl=False
):
    """
    從資料集網頁中尋找 ZIP 檔案下載網址。

    Parameters
    ----------
    page_url : str
        data.gov.tw 資料集頁面

    filename_pattern : str
        用來找到 ZIP 檔案名稱的 regex

    download_url_pattern : str
        用來找到政府下載 API 網址的 regex

    Returns
    -------
    list
        找到的 ZIP 資料
    """

    html = fetch_page(
        page_url,
        verify_ssl=verify_ssl
    )

    # 找出 ZIP 檔案名稱
    filenames = re.findall(
        filename_pattern,
        html,
        re.IGNORECASE
    )

    # 找出下載 API URL
    urls = re.findall(
        download_url_pattern,
        html,
        re.IGNORECASE
    )

    results = []

    for filename in filenames:
        # 在 HTML 中尋找這個檔名附近的下載網址
        filename_pos = html.find(filename)

        if filename_pos == -1:
            continue

        # 取檔名前後一段 HTML
        start = max(0, filename_pos - 2000)
        end = min(len(html), filename_pos + 2000)

        nearby_html = html[start:end]

        nearby_urls = re.findall(
            download_url_pattern,
            nearby_html,
            re.IGNORECASE
        )

        if nearby_urls:
            results.append({
                "filename": filename,
                "url": nearby_urls[0]
            })

    return results


def read_json_from_zip(zip_content):
    """
    從 ZIP bytes 中尋找第一個 JSON 檔案並讀取。

    Parameters
    ----------
    zip_content : bytes
        ZIP 檔案內容

    Returns
    -------
    dict / list
        JSON 資料
    """

    with zipfile.ZipFile(
        io.BytesIO(zip_content)
    ) as z:

        json_files = [
            name
            for name in z.namelist()
            if name.lower().endswith(".json")
        ]

        if not json_files:
            raise ValueError(
                "ZIP 檔案中找不到 JSON 檔案"
            )

        json_filename = json_files[0]

        with z.open(json_filename) as f:
            return json.load(f)


def fetch_json_from_zip(
    url,
    verify_ssl=False
):
    """
    下載 ZIP 並直接讀取其中的 JSON。
    """

    zip_content = download_file(
        url,
        verify_ssl=verify_ssl
    )

    return read_json_from_zip(
        zip_content
    )