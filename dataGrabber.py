from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from typing import List
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
from datetime import datetime

# Specify the path to chromedriver using Service
s = Service(r'D:\Uni\Projects\Projects\GoKartsScraping\important\chromedriver.exe')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def laps(racer: str, race: int) -> List:
    """
    race: the index of the wanted race (0 being most recent)
"""

    driver.get(f'https://www.racefacer.com/en/profile/' + racer +'/sessions')

    results_button = driver.find_elements(By.CLASS_NAME,'results-btn')
    results_button[race].click()


    position_finished = driver.find_elements(By.CLASS_NAME,'position')
    position = position_finished[race].text.strip()[:1]
    print(position)



    footer_buttons = driver.find_elements(By.CLASS_NAME, 'winners-footer')
    laps_button = footer_buttons[race].find_element(By.CLASS_NAME, 'open-laps-btn.middle')
    laps_button.click()

    #Finding date of race
    dates_header = driver.find_elements(By.CLASS_NAME,'minified-stat.date')
    date_class = dates_header[race].find_element(By.CLASS_NAME, "date")
    date = date_class.text.strip()
    
    time_class = dates_header[race].find_element(By.CLASS_NAME,"clock")
    time = time_class.text.strip()
    time = time[4:-2]


    laps_area = driver.find_elements(By.CLASS_NAME,'tab_laps')
    laps_area = laps_area[race]
    laps_table = laps_area.find_element(By.CLASS_NAME,'table_content')
    rows = laps_table.find_elements(By.CLASS_NAME,'row')

    laps = []
    for row in rows:
        lap_time_element = row.find_element(By.CSS_SELECTOR, '.time_laps.first')
        laps.append(lap_time_element.text.strip() if lap_time_element else None)

    return time,date,laps,position

racers = ["mitchell.whitten","mathew.stephen", "noah.thomson.4","josh.kolappillil","darian.king"]
record_set = []
for racer in racers:
    index = 0
    while True:
        try:
            time, date, raw_laps, position = laps(racer,index)
            print(raw_laps)
            for i in range(len(raw_laps)):
                if raw_laps[i] == "Return to Pit Box":
                    continue
                else:
                    record_set.append([time, date, racer, str(i+1), raw_laps[i], position])
            index += 1
        except:
            break


"""Formatting Database"""
column_names = ['Time of Race', 'Date', 'Racer', 'Lap', 'Lap Time', 'Position']
df = pd.DataFrame(record_set,columns=column_names)
df['RaceID'] = df['Time of Race'] + df['Date']

#Formatting lap times to seconds
def convert_to_seconds(time_str):
    minutes, seconds, milliseconds = [int(part) for part in time_str.replace('.', ':').split(':')]
    return minutes * 60 + seconds + milliseconds / 1000

def convert_id_readable(race_id):
    # Use regular expressions to extract the time and date parts
    match = re.match(r"(\d+):(\d+)(\d{2})\.(\d{2}\.\d{4})", race_id)
    
    if not match:
        return "Invalid format"

    # Extract the hour, minute, day, and the rest of the date parts
    hour, minute, day, month_year = match.groups()
    
    # Format the hour to 12-hour time and assume it is PM
    hour_int = int(hour)
    # If the hour is less than 12, we assume it's PM, otherwise, we convert to 12-hour format
    hour_formatted = f"{hour_int if hour_int <= 12 else hour_int - 12}"
    time_suffix = "pm" if hour_int <= 12 else "am"
    
    # Construct the time with the correct suffix
    time = f"{hour_formatted}:{minute}{time_suffix}"
    
    # Construct the date in the desired format
    date_formatted = datetime.strptime(f"{day}.{month_year}", "%d.%m.%Y").strftime("%d/%m/%Y")
    
    # Return the formatted string
    return f"{time} @ {date_formatted}"

#Applying the function to the lap times column
df['Lap Time Seconds'] = df['Lap Time'].apply(convert_to_seconds)
df['RaceID Name'] = df['RaceID'].apply(convert_id_readable)

# Split 'RaceID Name' into two columns 'Race Date' and 'Race Time'
df['Race Date'], df['Race Time'] = df['RaceID Name'].str.split('@',n=1).str

# Convert 'Race Date' to a sortable format
df['Race Date'] = pd.to_datetime(df['Race Date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

# Sort by 'Race Date' then 'Race Time'
df = df.sort_values(by=['Race Date', 'Race Time'])


df.to_csv('RaceTimes.csv', index=False)

# Close the browser
driver.quit()