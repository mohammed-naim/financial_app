import time

from flask import Flask
from models import db  # Ensure you import the necessary models
from sqlalchemy import text
import requests
import schedule

# Global variable to hold exchange rates
exchange_rates = {}


# Function to fetch exchange rates for specified currencies
def fetch_exchange_rates(reference_currency: str, currencies: list):
    """
    Fetches the current exchange rates for a list of specified currencies in relation to a reference currency.
    Stores the rates in a global dictionary.

    :param reference_currency: The currency to compare against (default is 'USD').
    :param currencies: List of currencies to get exchange rates for.
    """
    api_url = f"https://open.er-api.com/v6/latest/{reference_currency}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        exchange_rates[reference_currency] = {}
        # Store the exchange rates in the global dictionary
        for currency in currencies:
            exchange_rates[reference_currency][currency] = data['rates'].get(currency)

        print("Exchange rates fetched successfully.")
    except requests.RequestException as e:
        print(f"Error fetching exchange rates: {str(e)}")


# Function to calculate the profit or loss for an investment
def calculate_profit_or_loss(bought_amount, purchase_price, current_price):
    """
    Calculates the profit or loss based on the amount invested, purchase price, and the current price.

    :param bought_amount: The amount of currency units invested.
    :param purchase_price: The price per unit at the time of purchase.
    :param current_price: The current price per unit.
    :return: The profit or loss as a float with two decimal places.
    """
    initial_value = bought_amount * (1 / purchase_price)
    current_value = float(bought_amount) * float(current_price)
    profit_or_loss = float(current_value) - float(initial_value)

    return round(profit_or_loss, 2)


# Function to update current prices of all investments for all users
def update_all_user_investments():
    """
    Updates the current prices for all investments of all users.
    First fetches the exchange rates for specified currencies and stores them locally.
    """
    # Define the currencies to fetch rates for
    reference_currencies = ['USD', 'EUR', 'JOD', 'ILS']
    target_currencies = ['USD', 'EUR', 'JOD', 'ILS']

    # Fetch exchange rates for each reference-target currency pair
    for ref_currency in reference_currencies:
        fetch_exchange_rates(reference_currency=ref_currency, currencies=target_currencies)

    print("All required exchange rates fetched successfully.")

    for ref_currency in reference_currencies:
        for target_currency in target_currencies:
            # SQL statement to update all investments where currency and reference currency match
            exchange_rate = exchange_rates[target_currency][ref_currency]
            sql = text("""  UPDATE investments
                            SET current_price = :exchange_rate
                            WHERE currency = :target_currency AND reference_currency = :ref_currency """)

            # Execute the SQL statement
            db.session.execute(sql, {
                'exchange_rate': exchange_rate,
                'target_currency': target_currency,
                'ref_currency': ref_currency
            })

    db.session.commit()
    print("Updated investments for all users")


def run_investment_service(app: Flask):
    # Removed the infinite loop and sleep as scheduling will handle the interval
    # We can keep the `current_app.app_context()` for database access within the function
    with app.app_context():
        schedule.every(4).hours.do(update_all_user_investments)
        update_all_user_investments()
        while 1:
            schedule.run_pending()
            time.sleep(60 * 60)
