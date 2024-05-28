import mysql.connector
from mysql.connector import Error
import requests
from bs4 import BeautifulSoup
import time

# Function to connect to the database
def connect_to_database(host, user, password, database):
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if cnx.is_connected():
            print("Successfully connected to the database")
            return cnx
    except Error as e:
        print(f"Error while connecting to database: {e}")
        return None

# Function to fetch product data from the database
def fetch_product_data(cnx, url):
    cursor = cnx.cursor(dictionary=True)
    try:
        query = ("SELECT * FROM products WHERE product_url = %s")
        cursor.execute(query, (url,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error fetching product data: {e}")
        return None

# Function to compare prices
def compare_prices(current_price, stored_price):
    if current_price and stored_price:
        current_price = float(current_price.replace('€', '').replace(',', '.').strip())
        stored_price = float(stored_price)
        return current_price, stored_price, current_price - stored_price
    else:
        return None, None, None

# Main function
def main():
    host = '127.0.0.5'
    user = 'root'
    password = 'root'
    database = 'amazon'

    # Connect to the database
    cnx = connect_to_database(host, user, password, database)
    if cnx:
        # Get the URL of the product from the user
        product_url = input("Enter the URL of the product: ")

        # Fetch product data from the database
        product_data = fetch_product_data(cnx, product_url)
        if product_data:
            # Scrape current price from the web
            current_price = fetch_current_price(product_url)

            # Compare prices
            if current_price:
                current_price, stored_price, price_difference = compare_prices(current_price, product_data['price'])
                if current_price is not None:
                    print(f"Current price: {current_price}€")
                    print(f"Stored price: {stored_price}€")
                    print(f"Price difference: {price_difference}€")
            else:
                print("Failed to retrieve current price")
        else:
            print("Product data not found in the database")

        # Close the database connection
        cnx.close()
        print("Database connection closed")

# Function to fetch current price using Amazon API
def fetch_current_price(url):
    try:
        # Make a request to Amazon
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            # Check if the page contains a CAPTCHA challenge
            if 'captcha' in response.text.lower():
                # If CAPTCHA challenge detected, solve it using 2Captcha service
                captcha_solution = solve_captcha(response.text)
                if captcha_solution:
                    # Retry request with solved CAPTCHA
                    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                    return extract_price(response.text)
                else:
                    print("Failed to solve CAPTCHA")
            else:
                # No CAPTCHA challenge, proceed with extracting price
                return extract_price(response.text)
        else:
            print(f"Failed to retrieve webpage: {response.status_code}")
    except Exception as e:
        print(f"Error fetching current price: {e}")
    return None

# Function to solve CAPTCHA using 2Captcha service
def solve_captcha(html_content):
    # Extract CAPTCHA image URL from HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    captcha_img = soup.find('img', {'id': 'captcha-image'})
    if captcha_img:
        captcha_url = captcha_img['src']
        # Send CAPTCHA image to 2Captcha service for solving
        captcha_api_key = '336ceb892631cbd125fd62cf2319d7ea'
        response = requests.post('https://2captcha.com/in.php',
                                 data={'key': captcha_api_key, 'method': 'base64', 'body': captcha_url})
        if response.status_code == 200:
            # Extract CAPTCHA ID from response
            captcha_id = response.text.split('|')[1]
            # Poll 2Captcha service for solved CAPTCHA
            while True:
                time.sleep(5)  # Adjust polling interval as needed
                response = requests.get(f'https://2captcha.com/res.php?key={captcha_api_key}&action=get&id={captcha_id}')
                if 'OK' in response.text:
                    # CAPTCHA solved successfully, return solution
                    return response.text.split('|')[1]
                elif 'CAPCHA_NOT_READY' in response.text:
                    # CAPTCHA not yet solved, continue polling
                    continue
                else:
                    # Failed to solve CAPTCHA
                    return None
        else:
            print("Failed to submit captcha to 2Captcha")
    else:
        print("No CAPTCHA image found")
    return None

# Function to extract price from HTML content
def extract_price(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    price_element = soup.find('span', {'class': 'a-price'}).find('span', {'class': 'a-offscreen'})
    if price_element:
        return price_element.text.strip()
    else:
        print("Price element not found")
        return None

if __name__ == "__main__":
    main()
