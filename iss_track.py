import random
from time import sleep
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import smtplib
import pandas
import json
from concurrent.futures import ThreadPoolExecutor
import threading

# import environmental variables
load_dotenv()

# APIs:
ISS_API = os.environ.get('ISS_API')
SUNRISE_SUNSET_API = os.environ.get('SUNRISE_SUNSET_API')
CLOUD_COVER_API = os.environ.get('CLOUD_COVER_API')
LOCATION_API = os.environ.get('GEOLOCATION_API')

# Environmental Data
ERROR = 5
CLOUD_COVER_THRESHOLD = 50
NUMBER_OF_ISS_PASSES = 1
CHECK_INTERVAL = 60

# Email Data
MY_EMAIL = os.environ.get('MY_EMAIL')
APP_PASSWORD = os.environ.get('APP_PASSWORD')

# Global variables
user_list = []
data_report = []
iss_latitude = None
iss_longitude = None
cloud_coverage = None
num_of_checks = 0
num_of_passes = 0

# Ensure safe printing during multithread processing
print_lock = threading.Lock()

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

"""Attempts to connect to a specified API to retrieve relevant data
Returns api data in JSON format
If Connection Error/Timeout exception write a report, wait for random period of time,
and try to reattempt connection up to max number of retries"""
def connect_to_api(api, api_name, max_retries=15, **kwargs):
    # Try multiple attempts at connecting to api
    for attempt in range(max_retries):
        try:
            response = requests.get(url=api, **kwargs)
            response.raise_for_status()
            data = response.json()
        except ConnectionError:
            write_report(f"{api_name} Connection Error")
            sleep(random.randint(1, 70))
            continue
        except requests.exceptions.ConnectTimeout:
            write_report(f"{api_name} Connection Timeout")
            sleep(random.randint(1, 60))
            continue
        else:
            response.close()
            return data

    # If all API retries exceeded, write report and return None:
    write_report(f"{api_name} failed after {max_retries} attempts.")
    return None

"""Uses the users address to retrieve there latitude and longitude coordinates.
Returns a tuple in form: (latitude, longitude)."""
def get_user_coordinates(user_address):
    # Geoapify API parameters
    geolocation_param = {
        "apiKey": os.environ.get('GEOAPIFY_KEY'),
        "text": user_address,
        "format": "json"
    }

    # Get users latitude and longitude
    location_data = connect_to_api(api=LOCATION_API, api_name="Location Data", params=geolocation_param)

    # Check if location_data exceeds maximum retries or returns an invalid dict format
    if location_data is None or not location_data.get('results'):
        write_report(f"Location data retrieval failed for address: {user_address}")
        return None

    # Attempt to format the latitude and longitude data
    try:
        user_lat = float(location_data['results'][0]['lat'])
        user_long = float(location_data['results'][0]['lon'])
    # If exception, write report and return None for coordinates
    except (KeyError, IndexError, TypeError) as error:
        write_report(f"Geoapify API format error: {error}")
        return None

    # Reformat latitude and longitude as tupple coordinates
    user_location = (user_lat, user_long)
    return user_location

"""Reads user data from file, reformats data and generates user coordinates."""
def retrieve_user_data():
    # Attempt to read users in from json file
    try:
        with open("users.json", "r") as user_file:
            all_users = json.load(user_file)

    # If file not found, write report and exit app
    except FileNotFoundError:
        write_report("users.json not found.")
        print("ERROR: users.json file not found.")
        exit(1)

    # If decode error, write report and exit app
    except json.JSONDecodeError as the_error:
        write_report(f"users.json format error: {the_error}")
        print(f"ERROR: Invalid JSON in users.json: {the_error}")
        exit(1)

    # For each user retrieved from json.file
    for the_user in all_users:

        # Break address data into smaller parts delimited by ','
        address_data = the_user['Address'].split(",")
        # Remove whitespace from parts of address
        address_data = [part.strip() for part in address_data]

        # Validate user address data [suburb, city, country]
        if not len(address_data) == 3:
            write_report(f"Invalid Address: {the_user['Name']}: {the_user['Address']}")
            print(f"Invalid Address: {the_user['Name']}: {the_user['Address']}.\nSkipping user.")
            # Skip over user from file and move to next one
            continue

        # Get suburb and city data from address parts
        suburb = address_data[0]
        city = address_data[1]
        location_name = f"{suburb}, {city}"

        # Validate users addresses result in valid coordinates
        coordinates = get_user_coordinates(the_user['Address'])

        if coordinates is None:
            write_report(f"Could not retrieve coordinates for {the_user['Name']}.\nSkipping user.")
            # Skip over user from file and move to next one
            continue

        # Create a user profile
        user_profile = {
            "Name": the_user['Name'],
            "Email": the_user['Email'],
            "Coordinates": coordinates,
            "Location Name": location_name
        }

        # Add to programs user list
        user_list.append(user_profile)

"""Check if ISS is above (within a defined margin of error) of users latitude and longitude.
Returns True if ISS above, and False if not."""
def check_iss_overhead(user_coordinates):
    # Get ISS location Data
    global iss_latitude, iss_longitude

    # Retrieve lat and long from user coordinates
    lat = user_coordinates[0]
    long = user_coordinates[1]

    # Get current ISS location and reformat it
    iss_data = connect_to_api(api=ISS_API, api_name="ISS API", max_retries=10)

    # Check if iss_data api call exceeds maximum retries
    if iss_data is None:
        write_report("ISS API returned no data")
        return False

    # Try to format retrieved iss_data
    try:
        iss_latitude = float(iss_data['iss_position']['latitude'])
        iss_longitude = float(iss_data['iss_position']['longitude'])

    # If exceptions, write report and return False (ISS not above)
    except (KeyError, TypeError, ValueError) as error:
        write_report(f"ISS API Format Error: {error}")
        return False

    # Check if ISS is within ERROR margin of users latitude and longitude
    if (lat - ERROR) <= iss_latitude <= (lat + ERROR) and (long - ERROR) <= iss_longitude <= (long + ERROR):
        return True
    else:
        return False

"""Checks if the sky is currently dark at the users latitude and longitude.
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

    # Check if sunlight data api call has exceeded maximum retries
    if sun_data is None:
        write_report("Sunlight API returned no data")
        return False

    # Attempt to format retrieved sunlight data
    try:
        sunrise_hour = int(sun_data['results']['sunrise'].split("T")[1].split(":")[0])
        sunset_hour = int(sun_data['results']['sunset'].split("T")[1].split(":")[0])
    # If exceptions, write report and return false (not dark outside)
    except (KeyError, IndexError, ValueError) as error:
        write_report(f"Sunlight API format error: {error}")
        return False

    # Get the current time:
    current_time = datetime.now()
    current_hour = current_time.hour

    # Check if it is currently dark outside
    if current_hour >= sunset_hour or current_hour < sunrise_hour:
        return True
    else:
        return False

"""Retrieve the cloud cover percentage for users latitude and longitude.
Returns True if cloud cover less than CLOUD_COVER_THRESHOLD, or False otherwise."""
def check_cloud_coverage(user_coordinates):
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

    # Check if cloud cover api calls exceeded maximum retries
    if cloud_data is None:
        write_report("Cloud API returned no data")
        return False

    # Attempt to format retrieved cloud cover data
    try:
        cloud_coverage = cloud_data['current']['cloud_cover']
    # If exception, write report and return false (clear skies)
    except (KeyError, TypeError) as error:
        write_report(f"Cloud Cover API format error: {error}")
        return False

    # Check if cloud cover is below cloud cover threshold
    if cloud_coverage <= CLOUD_COVER_THRESHOLD:
        return True
    else:
        return False

"""Sends an email notification to the user.
Takes the user as input. If email connection fails, writes report to file."""
def send_notification(the_user):
    # Attempt to email the user to notify them
    try:
        # Open secure email connection and write email to notify users
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=APP_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=the_user['Email'],
                msg="Subject: The ISS is Above\n\n"
                    f"The International Space Station is flying above {the_user['Location Name']} right now!\n"
                    f"Look up!\n"
                    f"Current ISS Latitude: {iss_latitude}\n"
                    f"Current ISS Longitude: {iss_longitude}\n"
                    f"\nClear Skies!\n"
                    f"With love,\n"
                    f"Jay")

    # If exception caught write report and continue to next user
    except Exception as error:
        write_report(f"Email failed to send to {the_user['Email']}: {error}.")

"""Function to check if the conditions are good for spotting the ISS in the sky.
Sends an email notification when ISS passes overhead (within margin of error), 
the cloud coverage is low and the sky is dark. Additionally writes reports if only the ISS passes above."""
def search_the_sky(the_user):
    global num_of_checks, num_of_passes, print_lock

    num_of_checks+= 1
    coordinates = the_user['Coordinates']
    iss_above = check_iss_overhead(coordinates)
    clear_sky = check_cloud_coverage(coordinates)
    is_dark = check_if_dark(coordinates)

    # If the iss passes above, low cloud coverage and is dark outside
    if iss_above and clear_sky and is_dark:
        # Notify the user
        send_notification(the_user)
        # Increase the number of ISS passes
        num_of_passes += 1
        # Write report of ISS pass in good conditions
        write_report("Success: Notification sent")
        # Timeout program to ensure no duplicate notifications
        sleep(600)

    # if only the ISS passes above, write a report
    elif iss_above:
        write_report("ISS passed overhead")
        # Timeout for 5min
        sleep(300)

    # Otherwise print the user and current values for their position
    else:
        # Utilise a lock to ensure safe printing during multithread processes
        with print_lock:
            print(f"{the_user['Name']}:\n\t"
                f"ISS Above:   {iss_above}\n\t"
                f"Clear Skies: {clear_sky}\n\t"
                f"Dark Skies:  {is_dark}\n\n")


# Retrieve and format user data from file
retrieve_user_data()

# var to track number of successfully imported users
num_of_users = len(user_list)

# Report and display the number of users that are successfully imported
if num_of_users > 0:
    write_report(f"{len(user_list)} users data imported successfully from file")
    print(f"Users imported: {len(user_list)}\n")

# Otherwise write report, display error message and exit program
else:
    write_report(f"No user data has been imported. Exiting program...")
    print(f"No user data could be imported. Exiting program...")
    exit(1)

# Initialize report
write_report("Process START")
print("Process Starting...\n")

# While there are users and the number of tracked passes of ISS is less than or equal to set constant
while num_of_users > 0 and num_of_passes <= NUMBER_OF_ISS_PASSES:

    # Use a thread pool to check all users in user list in parallel
    # Use default max_workers value (for hosting on alternative platforms)
    with ThreadPoolExecutor() as executor:
        futures = []

        # Check the sky for each user in the user list
        for user in user_list:
            the_future = executor.submit(search_the_sky, user)
            futures.append(the_future)

    # Timeout between checks
    sleep(CHECK_INTERVAL)

# Write finalized report
write_report("Process END")
print("\nEnd Successful")


#TODO add feature to add additional users to file

#TODO ensure users do not get spam emailed, consider adding notification time stamps to user file

#TODO Create a simple encryption for user data written to and read from json file/Store data in encrypted form

#TODO Make getting location data more efficient
# (i.e only get location data for person the very first time then store to encrypted file)

#TODO Make get requests more robust to avoid timeout/connection errors

#TODO refine report feature - report logs (info on program) and data collection/observations to excel doc
# (future analysis/find patterns for planning in photography)
# Remove num checks (use indexing in excel rather)
# & consider removing num of iss passes and letting program run indefinitely

#TODO Create a real time map of ISS
