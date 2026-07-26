# streamlit_geolocation()は内部でkey="loc"を固定使用しており、同一画面で2回呼ぶと
# StreamlitDuplicateElementKeyになる。呼び出し箇所ごとに別keyを渡すため、
# ラップ前の生コンポーネント(_streamlit_geolocation)を直接呼び出す。
from streamlit_geolocation import _streamlit_geolocation

_DEFAULT_LOCATION = {
    "latitude": None, "longitude": None, "altitude": None,
    "accuracy": None, "altitudeAccuracy": None, "heading": None, "speed": None
}

def get_current_location(key: str):
    """
    位置情報取得ボタンを描画する。この関数自体がクリック可能なボタンを表示する。
    戻り値: {"lat": float, "lng": float} または None(未取得・拒否・非対応時)
    """
    location = _streamlit_geolocation(key=key, default=_DEFAULT_LOCATION)
    if isinstance(location, dict) and location.get("latitude") is not None and location.get("longitude") is not None:
        return {"lat": location["latitude"], "lng": location["longitude"]}
    return None

def reverse_geocode(gmaps_client, lat: float, lng: float) -> str:
    """緯度経度→地名文字列。失敗時は空文字。"""
    try:
        results = gmaps_client.reverse_geocode((lat, lng), language="ja")
        if results:
            return results[0].get("formatted_address", "")
    except Exception:
        pass
    return ""
