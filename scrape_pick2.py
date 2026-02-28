import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import sys


def scrape_pick2_ontario(start_year=2022, end_year=None, single_year=False):
    if single_year:
        end_year = start_year
    elif end_year is None:
        end_year = datetime.now().year

    base_url = "https://ca.lottonumbers.com/ontario/pick-games/numbers"

    all_results = []

    for year in range(start_year, end_year + 1):
        url = f"{base_url}/{year}"
        print(f"Scraping {year}...")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        month_rows = soup.find_all('td', class_='monthRow')

        for i, month_row in enumerate(month_rows):
            parent_tr = month_row.find_parent('tr')
            next_siblings = parent_tr.find_next_siblings('tr')

            current_date = None

            for tr in next_siblings:
                if tr.find('td', class_='monthRow'):
                    break

                date_cell = tr.find('td', class_='date-row')
                if date_cell:
                    date_text = date_cell.get_text(strip=True)
                    match = re.search(r'([A-Za-z]+)(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d+)\s+(\d{4})', date_text)
                    if match:
                        day_name = match.group(1)
                        month = match.group(2)
                        day = match.group(3)
                        year_str = match.group(4)
                        date_str = f"{month} {day} {year_str}"
                        try:
                            parsed_date = datetime.strptime(date_str, '%B %d %Y')
                            current_date = parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            pass

                if current_date:
                    cells = tr.find_all('td')
                    
                    if len(cells) >= 7:
                        pick2_midday = cells[1].get_text(strip=True)
                        pick2_evening = cells[4].get_text(strip=True)

                        if len(pick2_midday) == 2 and pick2_midday.isdigit():
                            all_results.append({
                                'date': current_date,
                                'session': 'Midday',
                                'digit1': pick2_midday[0],
                                'digit2': pick2_midday[1]
                            })

                        if len(pick2_evening) == 2 and pick2_evening.isdigit():
                            all_results.append({
                                'date': current_date,
                                'session': 'Evening',
                                'digit1': pick2_evening[0],
                                'digit2': pick2_evening[1]
                            })

        time.sleep(1)

    return all_results


def save_to_csv(results, filename='ontario_pick2_results.csv'):
    if not results:
        print("No results to save")
        return

    sorted_results = sorted(results, key=lambda x: (x['date'], 0 if x['session'] == 'Midday' else 1))

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'session', 'digit1', 'digit2'])
        writer.writeheader()
        writer.writerows(sorted_results)

    print(f"Saved {len(sorted_results)} results to {filename}")


if __name__ == '__main__':
    single_year = '--single-year' in sys.argv
    year = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 2022
    results = scrape_pick2_ontario(start_year=year, single_year=single_year)
    save_to_csv(results)
