import os
import requests


# =========================
# 基本設定
# =========================

LATITUDE = 24.9937
LONGITUDE = 121.3010

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


# =========================
# 取得天氣資料
# =========================

weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "daily": [
        "temperature_2m_max",
        "precipitation_probability_max"
    ],
    "timezone": "Asia/Taipei"
}

weather_response = requests.get(
    weather_url,
    params=weather_params,
    timeout=10
)

weather_response.raise_for_status()

weather_data = weather_response.json()

max_temperature = weather_data["daily"]["temperature_2m_max"][0]
max_rain_probability = weather_data["daily"]["precipitation_probability_max"][0]


# =========================
# 取得 AQI 資料
# =========================

air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

air_params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "hourly": "us_aqi",
    "timezone": "Asia/Taipei"
}

air_response = requests.get(
    air_url,
    params=air_params,
    timeout=10
)

air_response.raise_for_status()

air_data = air_response.json()

aqi_values = air_data["hourly"]["us_aqi"]

aqi = max(aqi_values)


# =========================
# 通勤建議
# =========================

recommendations = []

if max_rain_probability >= 60:
    recommendations.append("☔ 降雨機率達 60%，請記得攜帶雨傘。")

if max_temperature >= 33:
    recommendations.append("☀️ 最高溫達 33°C，請注意防曬並補充水分。")

if aqi >= 100:
    recommendations.append("😷 AQI 達 100，建議配戴口罩。")


if not recommendations:
    recommendations.append("✅ 今日天氣與空氣品質正常，適合外出通勤。")


# =========================
# 組合 Telegram 訊息
# =========================

message = f"""
🚗 智慧通勤風險通知

🌡️ 最高溫：{max_temperature}°C
☔ 最高降雨機率：{max_rain_probability}%
😷 AQI：{aqi}

【通勤建議】
"""

message += "\n".join(recommendations)


# =========================
# 傳送 Telegram
# =========================

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

telegram_data = {
    "chat_id": CHAT_ID,
    "text": message
}

telegram_response = requests.post(
    telegram_url,
    data=telegram_data,
    timeout=10
)

telegram_response.raise_for_status()

print("Telegram 通知發送成功！")
