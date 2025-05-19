import random
from time import sleep
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import smtplib
import pandas

# import environmental variables
load_dotenv()

# APIs:
ISS_API = os.environ.get('ISS_API')
SUNRISE_SUNSET_API = os.environ.get('SUNRISE_SUNSET_API')
CLOUD_COVER_API = os.environ.get('CLOUD_COVER_API')

# My Data
MY_LAT = float(os.environ.get('MY_LAT'))
MY_LONG = float(os.environ.get('MY_LONG'))

# Environmental Data
ERROR = 5
CLOUD_COVER_THRESHOLD = 50
NUMBER_OF_ISS_PASSES = 2

# Email Data
MY_EMAIL = os.environ.get('MY_EMAIL')
APP_PASSWORD = os.environ.get('APP_PASSWORD')
RECIPIENTS = ["andersonjason103@gmail.com", "kaylsb97@gmail.com", "jillmeaker777@gmail.com", "james@jesse-james.co.za",
              "guy.meaker@gmail.com"]

# Global variable
num_of_runs = 0
iss_latitude = None
iss_longitude = None
cloud_coverage = None
data_report = []


"""Writes and update a report in csv format"""
def write_report(report_message):
    the_time = datetime.now()
    # Reformat the date
    date = str(the_time.date())
    # Reformat the hour
    if the_time.hour < 10:
        present_hour = f"0{the_time.hour}"
    else:
        present_hour = the_time.hour
    # Reformat the minute
    if the_time.minute < 10:
        present_minute = f"0{the_time.minute}"
    else:
        present_minute = the_time.minute

    report_structure = {
        "Runtime": num_of_runs,
        "Date": date,
        "Time": f"{present_hour}:{present_minute}",
        "Status": f"{report_message}",
        "ISS Passes": num_of_passes,
    }
    # Create a csv with the updated report
    data_report.append(report_structure)
    dataframe = pandas.DataFrame(data_report)
    dataframe.to_csv("./ISS_Report.csv")


"""Attempts to connect to a specified API to access data
Returns data in JSON format
If Connection Error/Timeout exception write a report, wait for random period of time,
and try to reattempt connection up to max retries"""
def connect_to_api(api, api_name, max_retries=15, **kwargs):
    for attempt in range(max_retries):
        try:
            response = requests.get(url=api, **kwargs)
            response.raise_for_status()
            data = response.json()
        except ConnectionError:
            write_report(f"{api_name} Connection Error")
            sleep(random.randint(1, 30))
            continue
        except requests.exceptions.ConnectTimeout:
            write_report(f"{api_name} Connection Timeout")
            sleep(random.randint(1, 40))
            continue
        else:
            response.close()
            return data


"""Check if ISS is above (within a margin of error)
Returns True if ISS above, and False if not
Exception write a report and wait for random period of time before trying again"""
def check_iss_overhead():
    # Get ISS location Data
    global iss_latitude, iss_longitude
    iss_data = connect_to_api(api=ISS_API, api_name="ISS API", max_retries=10)
    iss_latitude = float(iss_data["iss_position"]["latitude"])
    iss_longitude = float(iss_data["iss_position"]["longitude"])
    print(f"lat: {iss_latitude}")
    print(f"long: {iss_longitude}")

    # Check if ISS is within ERROR margin of my latitude and longitude
    if (MY_LAT-ERROR) <= iss_latitude <= (MY_LAT+ERROR) and (MY_LONG-ERROR) <= iss_longitude <= (MY_LONG+ERROR):
        return True
    else:
        return False


"""Checks if the sky is currently dark at my latitude and longitude
Returns True if it is dark, False if not"""
def check_if_dark():
    sun_data_parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0
    }
    # Get sunlight data and reformat sunrise and sunset hour
    sun_data = connect_to_api(api=SUNRISE_SUNSET_API, api_name="Sunlight API", params=sun_data_parameters)
    sunrise_hour = int(sun_data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset_hour = int(sun_data["results"]["sunset"].split("T")[1].split(":")[0])

    # Get the time now:
    current_time = datetime.now()
    current_hour = current_time.hour

    # Check if it is currently dark outside
    if current_hour >= sunset_hour or current_hour < sunrise_hour:
        return True
    else:
        return False


"""Retrieve the cloud cover for my latitude and longitude
and returns True if less than CLOUD COVER THRESHOLD
If exception write a report and wait for random period of time before trying again"""
def check_not_cloudy():
    global cloud_coverage
    # Open-Metro Cloud cover API parameters
    cloud_parameters ={
        "latitude": MY_LAT,
        "longitude": MY_LONG,
        "current": "cloud_cover",
    }
    # Retrieve cloud coverage data, and reformat data
    cloud_data = connect_to_api(api=CLOUD_COVER_API, api_name="Cloud Cover API", params=cloud_parameters)
    cloud_coverage = cloud_data["current"]["cloud_cover"]

    # Check if cloud cover is below cloud cover threshold
    if cloud_coverage <= CLOUD_COVER_THRESHOLD:
        return True
    else:
        return False



# Continuously run every 30 seconds, until the ISS has gone overhead 3 times
# Check that the ISS above, that it is dark and low cloud cover
# If successful send email to notify recipients,
# write report, pause for ISS to pass over, and increase number of ISS passes
num_of_passes = 0
write_report("Process START")
print("Process Starting...\n")
while num_of_passes <= NUMBER_OF_ISS_PASSES:
    sleep(60)
    num_of_runs += 1
    iss_above = check_iss_overhead()
    is_dark = check_if_dark()
    clear_sky = check_not_cloudy()
    if iss_above and is_dark and clear_sky:
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=APP_PASSWORD)
            for recipient in RECIPIENTS:
                connection.sendmail(
                    from_addr=MY_EMAIL,
                    to_addrs=recipient,
                    msg="Subject: The ISS is Above\n\n"
                        "The International Space Station is flying above Plumstead right now!\n"
                        f"Look up!\n"
                        f"Current ISS Latitude: {iss_latitude}\n"
                        f"Current ISS Longitude: {iss_longitude}\n"
                        f"\nClear Skies!\n"
                        f"With love,\n"
                        f"Jay")
        num_of_passes+= 1
        print("\nSuccess: Notification sent\n")
        write_report("Success: Notification sent")
        sleep(600)
    elif iss_above:
        write_report("ISS passed overhead")
        print(f"ISS Above: {iss_above}, Dark: {is_dark}, Clear Sky: {clear_sky}")
        sleep(240)
    else:
        print(f"ISS Overhead: {iss_above}")
        print(f"Dark Outside: {is_dark}")
        print(f"Clear Skies:  {clear_sky}")

# Write final report
write_report("Process END")
print("\nEnd Successful")