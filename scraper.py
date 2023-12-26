import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import sys

def scrape_and_save_lottery_results(year, day_time, csv_filename):
    # Construct the URL
    url = f"https://www.lotteryleaf.com/on/pick-2-{day_time}/{year}"

    # Fetch the web page content
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # Find the table tag
    results = soup.find("table")

    # Extract Date and Winning Numbers
    data = []
    for row in results.find_all("tr")[1:]:  # Skip the header row
        columns = row.find_all("td")
        date = columns[0].get_text(strip=True)
        numbers = [li.get_text(strip=True) for li in columns[1].find_all("li")]
        data.append([date, day_time.capitalize()] + numbers)

    # Save data to CSV file
    with open(csv_filename, mode="a", newline="") as csvfile:  # Use "a" to append to the existing file
        csv_writer = csv.writer(csvfile)
        # Write data
        csv_writer.writerows(data)

    print(f"Data has been appended to {csv_filename}")


args = sys.argv
year = args[1]
day_time = "midday"
csv_filename = f"lottery_results_{year}.csv"
# create the csv file with header
with open(csv_filename, mode="w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Date", "Time", "Number1", "Number2"])
scrape_and_save_lottery_results(year, day_time, csv_filename)

# Example usage for evening results in 2020
day_time = "evening"
scrape_and_save_lottery_results(year, day_time, csv_filename)

# sort the csv file by date

df = pd.read_csv(csv_filename)
# convert the Date column to date format
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values(by=['Date'], inplace=True)
df.to_csv(csv_filename, index=False)
print("CSV file has been sorted by date")

