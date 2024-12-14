import time
import requests
from bs4 import BeautifulSoup
import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')


url = "https://www.the-numbers.com/movie/budgets/all"

output_file = "movies_budget.tsv"

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    header = ["Release Date", "Movie", "Production Budget", "Domestic Gross", "Worldwide Gross"]
    writer.writerow(header)
    
for i in range(11, 12):
    print(f"Scraping page {i}")
    url = f"https://www.the-numbers.com/movie/budgets/all/{i}01"
    response = requests.get(url)
    response.raise_for_status()  
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.find('table')

        
    rows = table.find_all('tr')[1:] 

    for row in rows:
        cols = row.find_all('td')
        movie_data = [
            cols[1].text.strip(),  
            cols[2].text.strip(),  
            cols[3].text.strip(),  
            cols[4].text.strip(), 
            cols[5].text.strip(),  
        ]
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(movie_data)
            print(f"Scraped: {movie_data[1]}")
        time.sleep(1)

    print(f"Data has been written to {output_file}")

