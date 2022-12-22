import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
chrome_options = Options();
chrome_options.add_experimental_option('detach',True)
url = 'https://www.glassdoor.co.uk/Job/fullstack-web-developer-jobs-SRCH_KO0,23.htm?fromAge=30'
driver = webdriver.Chrome(options=chrome_options)
driver.get(url);

job_cards = driver.find_elements(By.CLASS_NAME,'react-job-listing')
job_details = []
for job_card in job_cards:
    job_title = job_card.find_element(By.CSS_SELECTOR, '[data-test="job-link"').find_element(By.TAG_NAME,'span')
    job_location = job_card.find_element(By.CSS_SELECTOR, '[data-test="emp-location"]')
    # job_salary = job_card.find_element(By.CSS_SELECTOR, '[data-test="detailSalary"]')
    
    job = {
        'title': job_title.text,
        'location': job_location.text,
        # 'salary': job_salary.text
    }
    job_details.append(job)
    
print(job_details)