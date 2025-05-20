import random
from time import sleep
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import smtplib
import pandas
import json

# import environmental variables
load_dotenv()

# APIs:
ISS_API = os.environ.get('ISS_API')
SUNRISE_SUNSET_API = os.environ.get('SUNRISE_SUNSET_API')
CLOUD_COVER_API = os.environ.get('CLOUD_COVER_API')
LOCATION_API = os.environ.get('GEOLOCATION_API')

# My Data
MY_LAT = float(os.environ.get('MY_LAT'))
MY_LONG = float(os.environ.get('MY_LONG'))

# Environmental Data
ERROR = 5
CLOUD_COVER_THRESHOLD = 50
NUMBER_OF_ISS_PASSES = 1
CHECK_INTERVAL = 60

# Email Data
MY_EMAIL = os.environ.get('MY_EMAIL')
APP_PASSWORD = os.environ.get('APP_PASSWORD')



# Global variable
user_list = []
iss_latitude = None
iss_longitude = None
cloud_coverage = None
data_report = []
num_of_checks = 0
num_of_passes = 0



"""Writes and update a report in csv format"""
def write_report(report_message):
    global num_of_checks, num_of_passes

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
        "Runtime": num_of_checks,
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

    # If all API retries exceeded, write report and return None:
    write_report(f"{api_name} failed after {max_retries} attempts.")
    return None

"""Check if ISS is above (within a margin of error)
Returns True if ISS above, and False if not
Exception write a report and wait for random period of time before trying again"""
def check_iss_overhead(user_coordinates):
    # Get ISS location Data
    global iss_latitude, iss_longitude

    # Retrieve lat and long from user coordinates
    lat = user_coordinates[0]
    long = user_coordinates[1]

    # Get current ISS location and reformat it
    iss_data = connect_to_api(api=ISS_API, api_name="ISS API", max_retries=10)
    iss_latitude = float(iss_data["iss_position"]["latitude"])
    iss_longitude = float(iss_data["iss_position"]["longitude"])

    # Print current ISS lat and long to screen
    print(f"lat: {iss_latitude}")
    print(f"long: {iss_longitude}")

    # Check if ISS is within ERROR margin of users latitude and longitude
    if (lat - ERROR) <= iss_latitude <= (lat + ERROR) and (long - ERROR) <= iss_longitude <= (long + ERROR):
        return True
    else:
        return False


"""Checks if the sky is currently dark at my latitude and longitude
Returns True if it is dark, False if not"""
def check_if_dark(user_coordinates):
    # Retrieve lat and long from user coordinates
    lat = user_coordinates[0]
    long = user_coordinates[1]

    # Create sunrise-sunset api parameters
    light_data_parameters = {
        "lat": lat,
        "lng": long,
        "formatted": 0
    }

    # Get sunlight data and reformat sunrise and sunset hour
    sun_data = connect_to_api(api=SUNRISE_SUNSET_API, api_name="Sunlight API", params=light_data_parameters)
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
def check_not_cloudy(user_coordinates):
    global cloud_coverage

    # Retrieve lat and long from user coordinates
    lat = user_coordinates[0]
    long = user_coordinates[1]

    # Open-Metro Cloud cover API parameters
    cloud_parameters ={
        "latitude": lat,
        "longitude": long,
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


def get_user_coordinates(user_address):
    # Geoapify API parameters
    geolocation_param = {
        "apiKey": os.environ.get('GEOAPIFY_KEY'),
        "text": user_address,
        "format": "json"
    }

    # Get users latitude and longitude
    location_data = connect_to_api(api=LOCATION_API, api_name="Location Data", params=geolocation_param)
    user_lat = location_data["results"][0]["lat"]
    user_long = location_data["results"][0]["lon"]

    # Reformat latitude and longitude coordinates
    user_location = (user_lat, user_long)
    return user_location


def retrieve_user_data():
    # Extract user information from file
    with open("users.json", "r") as user_file:
        all_users = json.load(user_file)

        # For each user retrieved from json.file
        for the_user in all_users:

            # Break address data into smaller parts delimited by ','
            address_data = the_user["Address"].split(",")
            # Remove whitespace from parts of address
            address_data = [part.strip() for part in address_data]

            # Validate user address data
            if not len(address_data) == 3:
                write_report(f"Invalid Address: {the_user["Name"]}: {the_user["Address"]}")
                print(f"Invalid Address: {the_user["Name"]}: {the_user["Address"]}")
                # Skip over user from file and move to next one
                continue

            # Get suburb and city data from address parts
            suburb = address_data[0]
            city = address_data[1]
            location_name = f"{suburb}, {city}"

            # Create a user profile
            user_profile = {
                "Name": the_user["Name"],
                "Email": the_user["Email"],
                "Coordinates": get_user_coordinates(the_user["Address"]),
                "Location Name": location_name
            }

            # Add to programs user list
            user_list.append(user_profile)



# Retrieve and format user data from file
retrieve_user_data()

# Write report if successful
write_report("User data imported successfully from file")
print("User data successfully imported from file.\n")

# Continuously run every 30 seconds, until the ISS has gone overhead 3 times
# Check that the ISS above, that it is dark and low cloud cover
# If successful send email to notify recipients,
# write report, pause for ISS to pass over, and increase number of ISS passes
write_report("Process START")
print("Process Starting...\n")
while num_of_passes <= NUMBER_OF_ISS_PASSES:
    for user in user_list:
        sleep(CHECK_INTERVAL)
        num_of_checks += 1
        iss_above = check_iss_overhead(user["Coordinates"])
        is_dark = check_if_dark(user["Coordinates"])
        clear_sky = check_not_cloudy(user["Coordinates"])
        if iss_above and is_dark and clear_sky:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user=MY_EMAIL, password=APP_PASSWORD)
                connection.sendmail(
                    from_addr=MY_EMAIL,
                    to_addrs=user["Email"],
                    msg="Subject: The ISS is Above\n\n"
                        f"The International Space Station is flying above {user["Location Name"]} right now!\n"
                        f"Look up!\n"
                        f"Current ISS Latitude: {iss_latitude}\n"
                        f"Current ISS Longitude: {iss_longitude}\n"
                        f"\nClear Skies!\n"
                        f"With love,\n"
                        f"Jay")
            num_of_passes+= 1
            print("\nSuccess: Notification sent\n")
            write_report("Success: Notification sent")
            # Timeout program to ensure no duplicate notifications
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

#TODO add feature to run all users in different locations parallel

#TODO add feature to add additional users to file

#TODO Make getting location data more efficient
# (i.e only get location data for person the very first time then store to encrypted file)

#TODO Create a simple encryption for user data written to and read from json file/Store data in encrypted form

#TODO Make get requests more robust to avoid timeout/connection errors

#TODO refine report structure to make it more useful for some basic stats
# (future analysis/find patterns for planning in photography)

#TODO Create a real time map of ISS
