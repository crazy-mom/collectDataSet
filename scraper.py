#Import packages
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#dependency location
webdriver_path = '/usr/local/bin/chromedriver'
# Create a Service object
service = ChromeService(executable_path=webdriver_path)

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service = service)

# URL of the webpage to scrape
#LAST WORKING  URL url = 'https://www.linkedin.com/jobs/search?keywords=&location=Canada&geoId=101174742&f_JT=F%2CP%2CC%2CT&f_E=2%2C3%2C4&f_PP=100761630&f_TPR=r2592000&f_WT=1%2C3%2C2&position=1&pageNum=0&original_referer=https%3A%2F%2Fwww.linkedin.com%2Fjobs%2Fsearch%3Fkeywords%3D%26location%3DCanada%26geoId%3D101174742%26f_JT%3DF%252CP%252CC%252CT%26f_PP%3D100761630%26f_TPR%3Dr2592000%26f_E%3D2%252C3%252C4%26position%3D1%26pageNum%3D0'
#url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=&location=Greater%2BToronto%2BArea%2C%2BCanada&geoId=90009551&trk=public_jobs_jobs-search-bar_search-submit&start=25'
url = 'https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0'
driver.get(url)
driver.implicitly_wait(60)

#Scrapping script
n = driver.find_element(By.CLASS_NAME,'results-context-header__job-count').text

#removing any special character or comma using regular expression library
n = re.sub(r'[^\d]', '', n)
numberOfJobs = pd.to_numeric(n)

# Make a request to fetch the webpage content
response = requests.get(url)
print(response.text)

# Scroll to the bottom of the page to trigger lazy loading
SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Extract data from the webpage
soup = BeautifulSoup(response.text, 'html.parser')
jobs = []
for job_elem in soup.find_all(By.CLASS_NAME,'jobs-search__results-list'):
    title = job_elem.find(By.CLASS_NAME,'base-search-card__title').text.strip()
    sub_title = job_elem.find(By.CLASS_NAME,'base-search-card__subtitle').text.strip()
    location = job_elem.find(By.CLASS_NAME,'job-search-card__location').text.strip()
    date_posted = job_elem.find(By.CLASS_NAME,'job-search-card__listdate').text.strip()
    job_id = job_elem.find(By.CSS_SELECTOR, '[data-entity-urn]').text.strip()
    
    jobs.append({'Title': title, 'Location': location, 'Company Name' : sub_title, 'Date Posted': date_posted, 'Job_id': job_id})

# Close the WebDriver
driver.quit()

# Create a DataFrame and save it to a CSV file
df = pd.DataFrame(jobs)
df.to_csv('job_openings.csv', index=False)
