import os
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from bs4 import BeautifulSoup
#STEP 2
URL = "https://ycharts.com/companies/TSLA/revenues"

#Adding a user-agent to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

#Send a request to the website with the headers
response = requests.get(URL, headers=headers)
#Check if the request was successful
if response.status_code == 200:
    print("HTML content downloaded successfully!")
    Html_content = response.text  
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

#STEP 3
soup = BeautifulSoup(Html_content, 'html.parser')
'''print(soup.prettify())'''

#Find all tables in the HTML
tables = soup.find_all('table')

# Print the number of tables
#print(f"Number of tables found: {len(tables)}")

table = tables[0]  # Accessing the first table with the most recent info

#Extract the rows from the table
rows = table.find_all('tr')

dates = []
revenues = []

#Loop through the rows, skipping the first one (header row)
for row in rows[1:]:
    cols = row.find_all('td')  # Find all the columns in the row
    dates.append(cols[0].text.strip())  
    revenues.append(cols[1].text.strip())  

#Create a pandas DataFrame with the extracted data
Tesla_rev_df = pd.DataFrame({
    'Date': dates,
    'Revenue': revenues
})
#STEP 4 (Data cleaning)
Tesla_rev_df['Revenue'] = Tesla_rev_df['Revenue'].str.replace('B', '', regex=False)

Tesla_rev_df['Revenue'] = pd.to_numeric(Tesla_rev_df['Revenue'])

Tesla_rev_df.rename(columns={'Revenue': 'Revenue (in Billions)'}, inplace=True)
#Display the DataFrame
#print(Tesla_rev_df.head(10))

#STEP 5

#Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('tesla_revenue.db')  
cursor = conn.cursor()  
#Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tesla_revenue (
        Date TEXT,
        Revenue_in_Billions REAL
    )
''')

#Insert the data from the DataFrame directly into the SQLite table
for index, row in Tesla_rev_df.iterrows():
    cursor.execute(f'''
        INSERT INTO tesla_revenue (Date, Revenue_in_Billions) 
        VALUES ('{row['Date']}', {row['Revenue (in Billions)']})
    ''')
#Commit the changes and close the connection
conn.commit()  # Save the changes
conn.close()   # Close the connection to the database

# Display the DataFrame to confirm
print(Tesla_rev_df.head(5))

#STEP 6
#line plot
plt.figure(figsize=(10, 6))
plt.plot(Tesla_rev_df['Date'], Tesla_rev_df['Revenue (in Billions)'], marker='o', color='red')

plt.title('Tesla Quarterly Revenue Over Time')
plt.xlabel('Date')
plt.ylabel('Revenue (in Billions)')
plt.xticks(rotation=45)  # Rotate the x-axis labels to make them readable

plt.tight_layout()
plt.show()

plt.savefig('tesla_revenue_Line_plot.png')

#Bar plot
plt.figure(figsize=(10, 6))
plt.bar(Tesla_rev_df['Date'], Tesla_rev_df['Revenue (in Billions)'], color='green')

plt.title('Tesla Quarterly Revenue')
plt.xlabel('Date')
plt.ylabel('Revenue (in Billions)')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
plt.savefig('tesla_revenue_Bar_plot.png')

#Scatter plot
#Horizontal bar plot
plt.figure(figsize=(10, 6))
plt.barh(Tesla_rev_df['Date'], Tesla_rev_df['Revenue (in Billions)'], color='orange')

# Customize the plot
plt.title('Tesla Quarterly Revenue Comparison')
plt.xlabel('Revenue (in Billions)')
plt.ylabel('Date')

# Show the plot
plt.tight_layout()
plt.show()
plt.savefig('tesla_revenue_Horizontal_plot.png')