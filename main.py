import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from matplotlib import pyplot as plt

load_dotenv()

API_KEY = os.getenv("API_KEY")  # Set this in your .env as API_KEY=<your_api_key>

url = f"https://api.openweathermap.org/data/2.5/forecast?lat=6.67&lon=3.28&appid={API_KEY}"

temperatures = {}

if not API_KEY:
    print("Missing API_KEY environment variable. Please set API_KEY in your .env file.")
else:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "list" not in data or not isinstance(data["list"], list):
            print("Unexpected API response format: 'list' key not found.")
        else:
            for entry in data["list"]:
                dt = entry.get("dt")
                main = entry.get("main", {})
                temp_k = main.get("temp")

                if dt is None or temp_k is None:
                    continue

                date = datetime.fromtimestamp(dt)
                # Convert Kelvin to Celsius, round to 2 decimals
                temperatures[date] = round(temp_k - 273.15, 2)

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

# Build DataFrame first (do not assign the result of to_csv back to df)
df = pd.DataFrame.from_dict(temperatures, orient="index", columns=["Temperature"])

# Ensure the index is sorted chronologically and named
df.sort_index(inplace=True)
df.index.name = "Date"

# Compute temperature change
if not df.empty:
    df["Temperature_change"] = df["Temperature"].diff()
else:
    # Optional: keep the column so the CSV has consistent headers
    df["Temperature_change"] = pd.Series(dtype="float64")

# Finally, write to CSV (to_csv returns None; do not assign back to df)
df.to_csv("weather_data.csv", index=True, index_label="Date")
plt.plot(df.index, df["Temperature"])
# --- Replace your existing plt.plot() lines with this ---

# Create a figure with two subplots, sharing the same x-axis (time)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Plot 1: The original temperature forecast
ax1.plot(df.index, df["Temperature"], marker='o', linestyle='-', color='dodgerblue', label='Temperature (°C)')
ax1.set_title('5-Day Temperature Forecast for Agege, Nigeria')
ax1.set_ylabel('Temperature (°C)')
ax1.grid(True)
ax1.legend()

# Plot 2: The rate of change (the derivative)
ax2.bar(df.index, df["Temperature_change"], width=0.1, color='tomato', label='Change per 3 Hours')
ax2.set_title('Rate of Temperature Change (Derivative)')
ax2.set_ylabel('Change in Temp (°C)')
ax2.set_xlabel('Date and Time')
ax2.grid(True)
ax2.legend()

# Improve layout and show the plot
plt.tight_layout()
plt.show()