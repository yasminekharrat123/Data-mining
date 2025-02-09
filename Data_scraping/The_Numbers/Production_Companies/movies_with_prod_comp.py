import time
import requests
from bs4 import BeautifulSoup
import csv
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# scrape each production company with their movies

output_file = "movies_prod_comp_rest.tsv"
file_path = "production_companies_with_links.tsv"
failed_file = "failed_companies.tsv"

df = pd.read_csv(file_path, sep='\t')
companies= df.values.tolist()

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    header = ["Release Date", "Movie", "Company", "Production Budget", "Opening Weekend","Domestic Box Office", "Woldwide Box Office"]
    writer.writerow(header)

for company in companies[0:7094]:
    print(f"Scraping {company[0]}")
    print(f"URL: {company[4]}")
    try:
        response = requests.get(company[4])
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {company[0]}")
        with open(failed_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow([company[0], company[4]])
        continue
    

    response.raise_for_status()
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('tbody')
    if table:
        
        rows = table.find_all('tr')
        row = rows[0]
        
        cols = row.find_all('td')
        movie_comp = [
            cols[0].text.strip(), 
            cols[1].text.strip(),  
            company[0],
            cols[2].text.strip(), 
            cols[3].text.strip(), 
            cols[4].text.strip(),
            cols[5].text.strip(), 
        ]
            
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(movie_comp)
            print(f"Scraped: {movie_comp[0], movie_comp[2]}")

    print(f"Data has been written to {output_file}")


# with open(output_file, mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file, delimiter='\t')
#     header = ["Release Date", "Movie", "Company", "Production Budget", "Opening Weekend","Domestic Box Office", "Woldwide Box Office"]
#     writer.writerow(header)

# response = requests.get("https://www.the-numbers.com/movies/production-company/Split-Prism-Media")



response.raise_for_status()
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('tbody')
# print(table)
if table:
    
    rows = table.find_all('tr')
    # print(rows)
    for row in rows:
        cols = row.find_all('td')
        print(cols)
        movie_comp = [
            cols[0].text.strip(), 
            cols[1].text.strip(),  
            "Split Prism Media",
            cols[2].text.strip(), 
            cols[3].text.strip(), 
            cols[4].text.strip(),
            cols[5].text.strip(), 
        ]
        print(movie_comp)
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(movie_comp)
            print(f"Scraped: {movie_comp[0], movie_comp[2]}")

print(f"Data has been written to {output_file}")