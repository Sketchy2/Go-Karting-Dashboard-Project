from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from typing import List
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

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

    return time, date,laps

racers = ["mitchell.whitten","mathew.stephen", "noah.thomson.4","josh.kolappillil","darian.king"]
record_set = []
for racer in racers:
    index = 0
    while True:
        try:
            time, date, raw_laps = laps(racer,index)
            print(raw_laps)
            for i in range(len(raw_laps)):
                if raw_laps[i] == "Return to Pit Box":
                    continue
                else:
                    record_set.append([time, date, racer, str(i+1), raw_laps[i]])
            index += 1
        except:
            break


"""Formatting Database"""
column_names = ['Time of Race', 'Date', 'Racer', 'Lap', 'Lap Time']
df = pd.DataFrame(record_set,columns=column_names)
df['RaceID'] = df['Time of Race'] + df['Date']

#Formatting lap times to seconds
def convert_to_seconds(time_str):
    minutes, seconds, milliseconds = [int(part) for part in time_str.replace('.', ':').split(':')]
    return minutes * 60 + seconds + milliseconds / 1000

#Applying the function to the lap times column
df['Lap Time Seconds'] = df['Lap Time'].apply(convert_to_seconds)

df.to_csv('RaceTimes.csv', index=False)

# Close the browser
driver.quit()