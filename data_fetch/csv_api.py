import csv
import io
import re

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


def find_csv_urls(
    page_url,
    url_pattern,
    verify_ssl=False
):
    """
    從資料集頁面找出 CSV 下載網址。

    Parameters
    ----------
    page_url : str
        data.gov.tw 資料集頁面

    url_pattern : str
        CSV 下載網址的 regex

    Returns
    -------
    list[str]
        CSV 下載網址
    """

    html = fetch_page(
        page_url,
        verify_ssl=verify_ssl
    )

    urls = re.findall(
        url_pattern,
        html,
        re.IGNORECASE
    )

    # 去除重複網址
    unique_urls = list(
        dict.fromkeys(urls)
    )

    return unique_urls


def read_csv(
    content,
    encodings=None
):
    """
    將 CSV bytes 轉換成 list[dict]。

    會依序嘗試不同編碼。

    Parameters
    ----------
    content : bytes
        CSV 檔案內容

    encodings : list[str] | None
        要嘗試的編碼

    Returns
    -------
    list[dict]
        CSV 每一列資料
    """

    if encodings is None:
        encodings = [
            "utf-8-sig",
            "utf-8",
            "cp950",
            "big5"
        ]

    last_error = None

    for encoding in encodings:

        try:
            text = content.decode(
                encoding
            )

            reader = csv.DictReader(
                io.StringIO(text)
            )

            return list(reader)

        except UnicodeDecodeError as error:
            last_error = error

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"無法使用指定編碼讀取 CSV: {last_error}"
    )


def fetch_csv(
    url,
    verify_ssl=False,
    encodings=None
):
    """
    下載 CSV 並直接解析成 list[dict]。
    """

    content = download_file(
        url,
        verify_ssl=verify_ssl
    )

    return read_csv(
        content,
        encodings=encodings
    )