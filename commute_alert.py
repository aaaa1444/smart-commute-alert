print("智慧通勤風險通知系統啟動！")
import os
import requests
from datetime import datetime


# =========================
# 設定
# =========================

LATITUDE = os.getenv("LATITUDE", "25.0330")
LONGITUDE = os.getenv("LONGITUDE", "121.5654")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# =========================
# 取得天氣資料
# =========================

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": "temperature_2m_max,precipitation_probability_max",
        "timezone": "Asia/Taipei",
        "forecast_days": 1
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    try:
        max_temp = data["daily"]["temperature_2m_max"][0]
        rain_probability = data["daily"]["precipitation_probability_max"][0]
    except (KeyError, IndexError, TypeError):
        raise ValueError("天氣 API 回應格式錯誤")

    return max_temp, rain_probability


# =========================
# 取得空氣品質 AQI
# =========================

def get_air_quality():
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "us_aqi",
        "timezone": "Asia/Taipei",
        "forecast_days": 1
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    try:
        aqi_values = data["hourly"]["us_aqi"]
        aqi_values = [
            value for value in aqi_values
            if value is not None
        ]
    except (KeyError, TypeError):
        raise ValueError("空氣品質 API 回應格式錯誤")

    if not aqi_values:
        raise ValueError("找不到 AQI 資料")

    # 取今天預報資料中的最高 AQI
    max_aqi = max(aqi_values)

    return max_aqi


# =========================
# 建立通勤建議
# =========================

def create_advice(max_temp, rain_probability, aqi):

    advice = []

    # 條件 1：降雨機率
    if rain_probability >= 60:
        advice.append("☔ 降雨機率達 60%，提醒攜帶雨傘。")

    # 條件 2：最高溫
    if max_temp >= 33:
        advice.append("☀️ 最高溫達 33°C，請注意防曬並補充水分。")

    # 條件 3：AQI
    if aqi >= 100:
        advice.append("😷 AQI 達 100，建議配戴口罩並減少長時間戶外活動。")

    # 所有條件正常
    if not advice:
        advice.append("✅ 今日各項條件正常，適合外出通勤。")

    return advice


# =========================
# 傳送 Telegram
# =========================

def send_telegram(message):

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("缺少 TELEGRAM_BOT_TOKEN")

    if not TELEGRAM_CHAT_ID:
        raise ValueError("缺少 TELEGRAM_CHAT_ID")

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    response = requests.post(
        url,
        json=payload,
        timeout=10
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise ValueError(f"Telegram API 錯誤：{result}")


# =========================
# 主程式
# =========================

def main():

    print("開始取得通勤資料...")

    max_temp, rain_probability = get_weather()
    aqi = get_air_quality()

    advice = create_advice(
        max_temp,
        rain_probability,
        aqi
    )

    today = datetime.now().strftime("%Y-%m-%d")

    message = f"""🚦 智慧通勤風險通知

📅 日期：{today}

🌡️ 最高溫度：{max_temp}°C
🌧️ 最高降雨機率：{rain_probability}%
🌫️ AQI：{aqi}

📢 通勤建議：
"""

    message += "\n".join(advice)

    print(message)

    send_telegram(message)

    print("Telegram 通知已成功傳送。")


if __name__ == "__main__":
    main()
