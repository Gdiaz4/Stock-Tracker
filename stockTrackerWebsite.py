# imported packages
import pandas as pd
import streamlit as st
import requests
import json


# Functions
def get_first_words(file_path):  # retrieves the symbols of stocks from the 'r' txt file
    first_words_list = []  # Initialize an empty list to store first words

    # Open the text file in read mode
    with open(file_path, 'r') as file:
        # Read each line in the file
        for line in file:
            # Split the line into words
            words = line.split("|")
            # Check if the line is not empty and contains at least one word
            if words:
                # Get the first word from the line
                first_word = words[0]
                # Append the first word to the list
                first_words_list.append(first_word)

    return first_words_list


def fetch_stock_data(symbol, interval, api_key):  # returns the extracted data from the API call
    url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price_data = data.get('values', [])
        extracted_data = []
        for entry in price_data:
            extracted_entry = {
                'timestamp': entry.get('datetime', ''),
                'open': entry.get('open', 0.0),
                'high': entry.get('high', 0.0),
                'low': entry.get('low', 0.0),
                'close': entry.get('close', 0.0),
                'volume': entry.get('volume', 0)
            }
            extracted_data.append(extracted_entry)
        return extracted_data
    else:
        print(f'Error fetching data for {symbol}: {response.status_code}')
        return []


# Title that displays for streamlit website
st.title("Stock Price Tracker Web App")
st.header("Streamlit and TwelveData API")

# API KEY
api_key = "c38aa69db3fa491d9da733bb1f96cde1"

# sidebar
category = st.sidebar.selectbox("Choose a category",
                                ["Stock Price Tracker", "Currency Exchange", "Map", "Review our website!"])

# Category 1 - Stock Price Tracker
if category == "Stock Price Tracker":

    file_path = 'r.txt'
    result_list = get_first_words(file_path)
    result_list.insert(0, "")
    user_symbol = st.selectbox("Please Enter/Select Stock Symbol", options=result_list)
    interval_list = ["1min", "5min", "15min", "30min", "45min", "1h", "2h", "4h", "8h", "1day", "1week", "1month"]
    interval_list.insert(0, "")
    user_interval = st.selectbox('Please Enter/Select Interval e.g. 1min, 1h, 1day', options=interval_list)

    stock_data = fetch_stock_data(user_symbol, user_interval, api_key)

    if stock_data:
        st.success("Here is your stock data!")
        tabOne, tabTwo, tabThree = st.tabs(["Table", "Bar Chart", "Line Chart"])
        # Table Tab
        with tabOne:
            # Create DataFrame from the fetched data
            df = pd.DataFrame(stock_data)
            # Display data using Streamlit
            st.subheader(f'Stock Price Data for {user_symbol}')
            # st.dataframe(df)

            parameters = st.multiselect(
                'Select Desired Parameters',
                ["high", "low", "timestamp", "volume"])

            # Adding the dataframe element with the selected parameters by the user
            st.dataframe(df[['open', 'close'] + parameters], width=1000)
            # Bar Chart Tab
        with tabTwo:
            prices = [{'open': entry['open'], 'high': entry['high'], 'low': entry['low'], 'close': entry['close']} for
                      entry in stock_data]
            st.subheader(f'Stock Price Data for {user_symbol}')
            st.bar_chart(df.set_index('timestamp'), use_container_width=True)
            # Line Chart Tab
        with tabThree:
            timestamps = [entry['timestamp'] for entry in stock_data]
            highs = [entry['high'] for entry in stock_data]
            lows = [entry['low'] for entry in stock_data]
            opens = [entry['open'] for entry in stock_data]
            closes = [entry['close'] for entry in stock_data]
            volumes = [entry['volume'] for entry in stock_data]

            df = pd.DataFrame({'timestamp': timestamps, 'Highs': highs, 'Lows': lows, 'Opens': opens, 'Closes': closes,
                               'Volumes': volumes})

            checkboxes = {
                'Highs': st.checkbox("Show Highs"),
                'Lows': st.checkbox("Show Lows"),
                'Opens': st.checkbox("Show Opens"),
                'Closes': st.checkbox("Show Closes"),
                'Volumes': st.checkbox("Show Volumes")
            }
            # Filter data based on checkbox selection
            selected_columns = [key for key, value in checkboxes.items() if value]
            if selected_columns:
                selected_columns.insert(0, 'timestamp')  # Always include the timestamp column
                data_to_plot = df[selected_columns].set_index('timestamp')
                st.line_chart(data_to_plot)
            else:
                st.info("Please select at least one checkbox.")

# Category 2 - Currency Exchange
elif category == "Currency Exchange":
    st.subheader("Exchange Rate between Currencies")

    currency1 = st.selectbox(label="What currency do you want to covert?", options=(
        "AED", "ARS", "AUD", "BBD", "BHD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK",
        "DDK", "EGP", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "ISK", "JMD",
        "JOD", "JPY", "KES", "KRW", "KWD", "LBP", "LKR", "MAD", "MXN", "MYR", "NAD",
        "NOK", "NPR", "NZD", "OMR", "PAB", "PHP", "PKR", "PLN", "QAR", "RON", "RUB",
        "SAR", "SEK", "SGD", "THB", "TRY", "UAH"))

    currency2 = st.selectbox(label="What currency do you want to obtain?", options=(
        "AED", "ARS", "AUD", "BBD", "BHD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK",
        "DDK", "EGP", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "ISK", "JMD",
        "JOD", "JPY", "KES", "KRW", "KWD", "LBP", "LKR", "MAD", "MXN", "MYR", "NAD",
        "NOK", "NPR", "NZD", "OMR", "PAB", "PHP", "PKR", "PLN", "QAR", "RON", "RUB",
        "SAR", "SEK", "SGD", "THB", "TRY", "UAH"))

    amount = st.number_input("How much money do you want to covert?")

    if st.button("Submit"):
        url = f"https://api.twelvedata.com/currency_conversion?symbol={currency1}/{currency2}&amount={amount}&apikey={api_key}"

        response = requests.get(url)
        data = response.json()
        json_data = json.loads(response.text)

        st.success(f"Currencies: {json_data['symbol']}, Exchange Rate: {json_data['rate']}")
        st.success(f"Conversion from {currency1} to {currency2}: {amount} -> {json_data['amount']}")

# Category 3 - Map
elif category == "Map":
    st.header("The World's Ten Most Popular Stock Exchanges")
    st.subheader("This map marks the following exchanges:\n"
                 "1. New York Stock Exhange (NYSE)\n"
                 "2. Tokyo Stock Exchange (TSE)\n"
                 "3. London Stock Exchange (LSE)\n"
                 "4. Bombay Stock Exchange (BSE)\n"
                 "5. Shenzhen Stock Exchange (SZSE)\n"
                 "6. Euronext \n"
                 "7. Hong Kong Stock Exchange (HKEX)\n"
                 "8. Shanghai Stock Exchange (SSE)\n"
                 "9. Nasdaq \n"
                 "10. Toronto Stock Exchange (TSX)\n")

    stock_exchanges = {
        'NYSE': (40.7069, -74.0113),  # New York Stock Exchange
        'TSE': (35.6762, 139.6503),  # Tokyo Stock Exchange
        'LSE': (51.5151, -0.1444),  # London Stock Exchange
        'BSE': (19.0758, 72.8777),  # Bombay Stock Exchange
        'SZSE': (22.5431, 114.0579),  # Shenzhen Stock Exchange
        'Euronext': (48.8926, 2.2399),  # Euronext
        'HKEX': (22.2793, 114.1628),  # Hong Kong Stock Exchange
        'SSE': (31.2304, 121.4737),  # Shanghai Stock Exchange
        'Nasdaq': (37.7749, -122.4194),  # Nasdaq
        'TSX': (43.65107, -79.347015)  # Toronto Stock Exchange
    }

    # Create a DataFrame with the stock exchange coordinates
    df = pd.DataFrame(stock_exchanges.values(), index=stock_exchanges.keys(), columns=['lat', 'lon'])

    # Display the map with markers for stock exchanges
    st.map(df)
# Category 4 - Website Review
elif category == "Review our website!":
    with st.form("Review Us", clear_on_submit=True):

        rating = st.slider("Rate the quality of the app", 1, 5)

        review = st.text_area("Please write a review below")

        submit = st.form_submit_button("Submit")

    if submit:
        st.success("Thank you for your review, have a nice day!")

