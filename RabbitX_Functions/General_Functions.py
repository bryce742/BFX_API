# This file was designed for use in google collab. Ensure you have your relevant key-value pairs in secrets on collab
# Make sure the client is installed: $pip install git+https://github.com/rabbitx-io/rabbitx-python-client.git

import requests
import pandas as pd
from rabbitx.client import Client, CandlePeriod, OrderSide, OrderType, OrderStatus
import pytz
from pytz import utc, timezone
import time
from datetime import datetime, timezone, timedelta
from google.colab import userdata

#__________________________API Endpoints______________________________________________

rest_mainnet_ep = 'https://api.prod.rabbitx.io'
rest_testnet_ep = 'https://api.testnet.rabbitx.io'


#__________________________Initialize Client______________________________________________

from google.colab import userdata
API_KEY = userdata.get('API_KEY')
API_SECRET = userdata.get('API_SECRET')
PUBLIC_JWT = userdata.get('PUBLIC_JWT')
PRIVATE_JWT = userdata.get('PRIVATE_JWT')
client = Client(
    api_url='https://api.prod.rabbitx.io',
    api_key=API_KEY,
    api_secret=API_SECRET,
    public_jwt=PUBLIC_JWT,
    private_jwt=PRIVATE_JWT
)

#_____________________Get basic market info as a df___________________________________________________

def get_market_info(base_url, market_id=None):
    market_info_ep = f"{base_url}/markets"
    params = {}
    if market_id:
        params['market_id'] = market_id

    # Make the GET request to the endpoint with optional parameters
    response = requests.get(market_info_ep, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()

        # Check if the response was successful and contains the expected 'result' key
        if data.get('success') and 'result' in data:
            # Convert the list of market dictionaries to a pandas DataFrame
            return pd.DataFrame(data['result'])
        else:
            print("No market data found or response marked as unsuccessful.")
    else:
        print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")

    # Return an empty DataFrame if there were issues
    return pd.DataFrame()

# Example use
market_id = 'W-USD'
df = get_market_info(rest_mainnet_ep, market_id=market_id)
df

#_____________________Only return bid, ask, market price, and time_______________________________________

def get_market_simplified(base_url, market_id=None):
    market_info_ep = f"{base_url}/markets"
    params = {}
    if market_id:
        params['market_id'] = market_id

    # Make the GET request to the endpoint with optional parameters
    response = requests.get(market_info_ep, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()

        # Check if the response was successful and contains the expected 'result' key
        if data.get('success') and 'result' in data:
            # Convert the list of market dictionaries to a pandas DataFrame
            df = pd.DataFrame(data['result'])
            # Extract specific columns as a dictionary from the first row
            if not df.empty:
                return {
                    'best_bid': df.at[0, 'best_bid'],
                    'best_ask': df.at[0, 'best_ask'],
                    'market_price': df.at[0, 'market_price'],
                    'last_update_time': df.at[0, 'last_update_time']
                }
            else:
                print("DataFrame is empty.")
        else:
            print("No market data found or response marked as unsuccessful.")
    else:
        print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")

    # Return None or an empty dictionary if there were issues
    return {}

# Example use
market_id = 'W-USD'
market_data = get_market_simplified(rest_mainnet_ep, market_id=market_id)
market_data

#__________________get_market_simplified but as normal time____________________________________________

def convert_microseconds_to_cst(microseconds):
  seconds = int(microseconds / 1000000)
  timestamp = datetime.utcfromtimestamp(seconds)
  utc_datetime = timestamp.replace(tzinfo=utc)
  cst_timezone = timezone('America/Chicago')
  cst_datetime = utc_datetime.astimezone(cst_timezone)
  return cst_datetime

# Example usage
microseconds = 1651476400000000
cst_time = convert_microseconds_to_cst(microseconds)

print(f"UTC time: {cst_time.astimezone(utc)}")
print(f"CST time: {cst_time}")

def get_market_simplified_with_timezone(base_url, market_id=None):
    market_info_ep = f"{base_url}/markets"
    params = {}
    if market_id:
        params['market_id'] = market_id

    # Make the GET request to the endpoint with optional parameters
    response = requests.get(market_info_ep, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()

        # Check if the response was successful and contains the expected 'result' key
        if data.get('success') and 'result' in data:
            # Convert the list of market dictionaries to a pandas DataFrame
            df = pd.DataFrame(data['result'])

            # Check if DataFrame is empty
            if not df.empty:
                # Extract timestamp
                timestamp = df.at[0, 'last_update_time']

                # Convert timestamp to CST and UTC using the function
                cst_time = convert_microseconds_to_cst(int(timestamp))
                utc_time = cst_time.astimezone(utc)

                # Format timestamps for readability (change format as desired)
                formatted_cst_time = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                formatted_utc_time = utc_time.strftime("%Y-%m-%d %H:%M:%S %Z")

                # Return dictionary with market data and converted times
                return {
                    'best_bid': df.at[0, 'best_bid'],
                    'best_ask': df.at[0, 'best_ask'],
                    'market_price': df.at[0, 'market_price'],
                    'last_update_time': df.at[0, 'last_update_time'],
                    'last_update_time_cst': formatted_cst_time,
                    'last_update_time_utc': formatted_utc_time
                }
            else:
                print("DataFrame is empty.")
        else:
            print("No market data found or response marked as unsuccessful.")
    else:
        print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")

    return {}

#Example Usage
market_id = 'W-USD'
market_data = get_market_simplified_with_timezone(rest_mainnet_ep, market_id=market_id)
market_data

#_________________________Orders______________________________________________

def create_Long_Limit(marketid,price,size):
    result = client.orders.create(market_id=marketid, price=price, side=OrderSide.LONG, size=size, type_=OrderType.LIMIT)
    assert result['status'] == 'processing'
def create_Short_Limit(marketid,price,size):
    result = client.orders.create(market_id=marketid, price=price, side=OrderSide.SHORT, size=size, type_=OrderType.LIMIT)
    assert result['status'] == 'processing'

# cancel all orders
def cancel_all():
    result = client.orders.cancel_all()
    print(result)

#get current positions
positions = client.positions.list()
print(positions)

# get filled orders
fills = client.fills.list()
print(fills[0])
print(fills[0]['timestamp'])