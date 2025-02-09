import time
import requests
from bs4 import BeautifulSoup
import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')

# scrape all the production companies with their likns

url = "https://www.the-numbers.com/movies/production-companies/#production_companies_overview=p1:od1"
output_file = "production_companies.tsv"

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    header = ["Company", "Number of Movies", "Total Domestic Box Office", "Total Worldwide Box Office", "URL"]
    writer.writerow(header)

for i in range(0, 174):
    print(f"Scraping page {i}")
    url = f"https://www.the-numbers.com/movies/production-companies/#production_companies_overview=p{i}:od1"
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')[1:]

    for row in rows:
        cols = row.find_all('td')
        
        company_col = cols[0].find('a')
        href = company_col['href'].strip()
        company_url = f"https://www.the-numbers.com{href}"

        prod_comp = [
            cols[0].text.strip(), 
            cols[1].text.strip(),  
            cols[2].text.strip(), 
            cols[3].text.strip(),  
            company_url,  
        ]
        
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(prod_comp)
            print(f"Scraped: {prod_comp[0]}")
        time.sleep(1)

    print(f"Data has been written to {output_file}")
