# app.py
# This is a simple Python web app using Flask to create a trading journal.
# It reads and writes trade data to a CSV file to persist the information.

import os
import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Define the filename for our data.
# This will be created in the same directory as the script.
DATA_FILE = 'trading_journal.csv'

# Ensure the data file exists with the correct headers.
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Sl No.", "Script Name", "Time", "Long/Short", "Entry Price", "SL",
            "Quantity", "% of Account Risked", "Target Price", "Exit Price",
            "Exit Time", "R/R", "P/L", "Did I followd MY RUES?"
        ])

def get_journal_data():
    """Reads all trade data from the CSV file and returns it as a list of dictionaries."""
    try:
        with open(DATA_FILE, 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        return []

def calculate_summary(data):
    """
    Calculates summary statistics based on the provided trade data.
    Returns a dictionary of key metrics.
    """
    if not data:
        return {
            "Total Number of Trades": 0,
            "Total Number of Winning Trades": 0,
            "Total Number of Losing Trades": 0,
            "Total Number of Break Even Trades": 0,
            "Total Number of Win Rate in %": "0.00",
            "Total Number of Lose Rate in %": "0.00",
            "Largest Winning Trade": 0,
            "Largest Losing Trade": 0,
            "Total P/L": 0,
        }

    df = pd.DataFrame(data)
    # Convert 'P/L' column to numeric, handling potential errors
    df['P/L'] = pd.to_numeric(df['P/L'], errors='coerce').fillna(0)

    total_trades = len(df)
    winning_trades = len(df[df['P/L'] > 0])
    losing_trades = len(df[df['P/L'] < 0])
    break_even_trades = len(df[df['P/L'] == 0])

    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    lose_rate = (losing_trades / total_trades) * 100 if total_trades > 0 else 0

    largest_win = df['P/L'].max() if winning_trades > 0 else 0
    largest_loss = df['P/L'].min() if losing_trades > 0 else 0
    total_pl = df['P/L'].sum()

    summary = {
        "Total Number of Trades": total_trades,
        "Total Number of Winning Trades": winning_trades,
        "Total Number of Losing Trades": losing_trades,
        "Total Number of Break Even Trades": break_even_trades,
        "Total Number of Win Rate in %": f"{win_rate:.2f}",
        "Total Number of Lose Rate in %": f"{lose_rate:.2f}",
        "Largest Winning Trade": largest_win,
        "Largest Losing Trade": largest_loss,
        "Total P/L": total_pl,
    }
    return summary

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles the main page, displaying the journal and summary, and processing new entries.
    """
    if request.method == 'POST':
        # Get data from the form
        sl_no = len(get_journal_data()) + 1
        new_entry = {
            "Sl No.": sl_no,
            "Script Name": request.form['script_name'],
            "Time": request.form['time'],
            "Long/Short": request.form['long_short'],
            "Entry Price": request.form['entry_price'],
            "SL": request.form['sl'],
            "Quantity": request.form['quantity'],
            "% of Account Risked": request.form['account_risked'],
            "Target Price": request.form['target_price'],
            "Exit Price": request.form['exit_price'],
            "Exit Time": request.form['exit_time'],
            "R/R": request.form['rr'],
            "P/L": request.form['pl'],
            "Did I followd MY RUES?": request.form['follow_rules']
        }

        # Append new entry to the CSV file
        with open(DATA_FILE, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=new_entry.keys())
            writer.writerow(new_entry)

        # Redirect to the same page to show the updated data
        return redirect(url_for('index'))

    # If it's a GET request, display the page with current data
    journal_data = get_journal_data()
    summary_data = calculate_summary(journal_data)

    return render_template('index.html', journal_data=journal_data, summary_data=summary_data)


# The HTML template for the front-end
@app.route('/index.html')
def index_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trading Journal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f3f4f6;
            }
            .container {
                max-width: 1200px;
            }
            input[type="text"], input[type="number"] {
                @apply w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150;
            }
            select {
                @apply w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150;
            }
            th, td {
                @apply p-2 text-left;
            }
            th {
                @apply bg-gray-200 sticky top-0;
            }
            tr:nth-child(even) {
                @apply bg-gray-50;
            }
            .summary-box {
                @apply bg-white p-6 rounded-xl shadow-md transition duration-300 hover:shadow-lg;
            }
            .form-section {
                @apply bg-white p-8 rounded-xl shadow-lg mb-8;
            }
            .table-container {
                max-height: 500px; /* Adjust height as needed */
                overflow-y: auto;
            }
        </style>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="container mx-auto">
            <!-- Header Section -->
            <header class="text-center mb-12">
                <h1 class="text-4xl md:text-5xl font-extrabold text-gray-800 tracking-tight mb-2">Tool For Every Traders</h1>
                <p class="text-lg text-gray-500">Track your progress, analyze your trades, and become a better trader.</p>
            </header>

            <!-- Summary Section -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-12">
                <div class="summary-box">
                    <h3 class="font-bold text-gray-600 mb-2">Total Trades</h3>
                    <p class="text-4xl font-extrabold text-blue-600">{{ summary_data['Total Number of Trades'] }}</p>
                </div>
                <div class="summary-box">
                    <h3 class="font-bold text-gray-600 mb-2">Total P/L</h3>
                    <p class="text-4xl font-extrabold {% if summary_data['Total P/L'] > 0 %}text-green-600{% elif summary_data['Total P/L'] < 0 %}text-red-600{% else %}text-gray-600{% endif %}">{{ summary_data['Total P/L'] }}</p>
                </div>
                <div class="summary-box">
                    <h3 class="font-bold text-gray-600 mb-2">Win Rate</h3>
                    <p class="text-4xl font-extrabold text-purple-600">{{ summary_data['Total Number of Win Rate in %'] }}%</p>
                </div>
                <div class="summary-box">
                    <h3 class="font-bold text-gray-600 mb-2">Largest Win</h3>
                    <p class="text-xl font-bold text-green-500">{{ summary_data['Largest Winning Trade'] }}</p>
                    <h3 class="font-bold text-gray-600 mb-2">Largest Loss</h3>
                    <p class="text-xl font-bold text-red-500">{{ summary_data['Largest Losing Trade'] }}</p>
                </div>
            </div>

            <!-- Trade Entry Form -->
            <div class="form-section">
                <h2 class="text-2xl font-bold text-gray-800 mb-6">Add New Trade</h2>
                <form method="POST" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    <div>
                        <label for="script_name" class="block text-sm font-medium text-gray-700">Script Name</label>
                        <input type="text" id="script_name" name="script_name" required>
                    </div>
                    <div>
                        <label for="time" class="block text-sm font-medium text-gray-700">Time</label>
                        <input type="text" id="time" name="time">
                    </div>
                    <div>
                        <label for="long_short" class="block text-sm font-medium text-gray-700">Long/Short</label>
                        <select id="long_short" name="long_short" required>
                            <option value="">Select...</option>
                            <option value="Long">Long</option>
                            <option value="Short">Short</option>
                        </select>
                    </div>
                    <div>
                        <label for="entry_price" class="block text-sm font-medium text-gray-700">Entry Price</label>
                        <input type="number" step="0.01" id="entry_price" name="entry_price" required>
                    </div>
                    <div>
                        <label for="sl" class="block text-sm font-medium text-gray-700">Stop Loss</label>
                        <input type="number" step="0.01" id="sl" name="sl">
                    </div>
                    <div>
                        <label for="quantity" class="block text-sm font-medium text-gray-700">Quantity</label>
                        <input type="number" id="quantity" name="quantity" required>
                    </div>
                    <div>
                        <label for="account_risked" class="block text-sm font-medium text-gray-700">% of Account Risked</label>
                        <input type="text" id="account_risked" name="account_risked">
                    </div>
                    <div>
                        <label for="target_price" class="block text-sm font-medium text-gray-700">Target Price</label>
                        <input type="number" step="0.01" id="target_price" name="target_price">
                    </div>
                    <div>
                        <label for="exit_price" class="block text-sm font-medium text-gray-700">Exit Price</label>
                        <input type="number" step="0.01" id="exit_price" name="exit_price" required>
                    </div>
                    <div>
                        <label for="exit_time" class="block text-sm font-medium text-gray-700">Exit Time</label>
                        <input type="text" id="exit_time" name="exit_time">
                    </div>
                    <div>
                        <label for="rr" class="block text-sm font-medium text-gray-700">R/R</label>
                        <input type="text" id="rr" name="rr">
                    </div>
                    <div>
                        <label for="pl" class="block text-sm font-medium text-gray-700">P/L</label>
                        <input type="number" step="0.01" id="pl" name="pl" required>
                    </div>
                    <div class="col-span-1 md:col-span-3 lg:col-span-4">
                        <label for="follow_rules" class="block text-sm font-medium text-gray-700">Did I follow MY RULES?</label>
                        <select id="follow_rules" name="follow_rules">
                            <option value="Yes">Yes</option>
                            <option value="No">No</option>
                        </select>
                    </div>
                    <div class="col-span-1 md:col-span-3 lg:col-span-4 flex justify-end">
                        <button type="submit" class="bg-blue-600 text-white font-bold py-3 px-6 rounded-xl shadow-md hover:bg-blue-700 transition duration-200">
                            Add Trade
                        </button>
                    </div>
                </form>
            </div>

            <!-- Trading Journal Table -->
            <div class="bg-white p-8 rounded-xl shadow-lg">
                <h2 class="text-2xl font-bold text-gray-800 mb-6">Trade History</h2>
                <div class="table-container">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50 sticky top-0">
                            <tr>
                                <th scope="col">Sl No.</th>
                                <th scope="col">Script Name</th>
                                <th scope="col">Time</th>
                                <th scope="col">Long/Short</th>
                                <th scope="col">Entry Price</th>
                                <th scope="col">SL</th>
                                <th scope="col">Quantity</th>
                                <th scope="col">% of Account Risked</th>
                                <th scope="col">Target Price</th>
                                <th scope="col">Exit Price</th>
                                <th scope="col">Exit Time</th>
                                <th scope="col">R/R</th>
                                <th scope="col">P/L</th>
                                <th scope="col">Did I followd MY RUES?</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {% for trade in journal_data %}
                            <tr>
                                <td>{{ trade['Sl No.'] }}</td>
                                <td>{{ trade['Script Name'] }}</td>
                                <td>{{ trade['Time'] }}</td>
                                <td>{{ trade['Long/Short'] }}</td>
                                <td>{{ trade['Entry Price'] }}</td>
                                <td>{{ trade['SL'] }}</td>
                                <td>{{ trade['Quantity'] }}</td>
                                <td>{{ trade['% of Account Risked'] }}</td>
                                <td>{{ trade['Target Price'] }}</td>
                                <td>{{ trade['Exit Price'] }}</td>
                                <td>{{ trade['Exit Time'] }}</td>
                                <td>{{ trade['R/R'] }}</td>
                                <td class="font-bold {% if trade['P/L']|float > 0 %}text-green-600{% elif trade['P/L']|float < 0 %}text-red-600{% else %}text-gray-600{% endif %}">{{ trade['P/L'] }}</td>
                                <td>{{ trade['Did I followd MY RUES?'] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% if not journal_data %}
                <p class="text-center text-gray-500 py-8">No trades recorded yet. Add your first trade above!</p>
                {% endif %}
            </div>

            <!-- Footer Section -->
            <footer class="text-center text-gray-500 mt-12 text-sm">
                <p>&copy; 2025 Trading Journal App. All rights reserved.</p>
            </footer>

        </div>
    </body>
    </html>
    """
if __name__ == '__main__':
    app.run(debug=True)

