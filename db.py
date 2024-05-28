import json
import mysql.connector
from mysql.connector import Error

def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("JSON data loaded successfully")
            print(json.dumps(data, indent=4))  # Pretty print JSON data
            return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def connect_to_database(host, user, password, database):
    """Establish a database connection."""
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

def clean_price(price_str):
    """Clean and format the price string."""
    if price_str is None:
        return None

    # Remove non-numeric characters except for decimal point
    cleaned_price = ''.join(char for char in price_str if char.isdigit() or char == '.')

    # Convert to float
    try:
        return float(cleaned_price)
    except ValueError:
        print(f"Error converting price: {price_str}")
        return None

def insert_data(cnx, data):
    """Insert data into the MySQL table."""
    cursor = cnx.cursor()
    add_product = ("INSERT INTO products (category, product_name, price, product_url, registration_date) VALUES (%s, %s, %s, %s, NOW())")
    try:
        for entry in data:
            # Check if all required keys are present
            if 'category' in entry and 'product_name' in entry and 'product_url' in entry:
                price_str = entry.get('price')
                if price_str is not None:
                    price = clean_price(price_str)
                    if price is not None:
                        cursor.execute(add_product, (entry['category'], entry['product_name'], price, entry['product_url']))
                        print(f"Inserted: {entry['category']}, {entry['product_name']}, {price}, {entry['product_url']}")
                    else:
                        print(f"Skipping entry due to invalid price: {entry}")
                else:
                    print(f"Skipping entry due to missing price: {entry}")
            else:
                print(f"Skipping entry due to missing keys: {entry}")
        cnx.commit()
        print("Data successfully inserted into the table")
    except Error as e:
        print(f"Error while inserting data: {e}")
        cnx.rollback()
    finally:
        cursor.close()

def main():
    file_path = 'amazon_scraper/output.json'
    host = '127.0.0.5'
    user = 'root'
    password = 'root'
    database = 'amazon'
    
    # Load JSON data
    json_data = load_json(file_path)
    if not json_data:
        print("No data to insert, exiting.")
        return
    
    # Connect to the database
    cnx = connect_to_database(host, user, password, database)
    if cnx:
        # Insert data into the database
        insert_data(cnx, json_data)
        # Close the connection
        cnx.close()
        print("Database connection closed")

if __name__ == "__main__":
    main()
