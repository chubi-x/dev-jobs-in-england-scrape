from re import search
from typing import List
import pandas as pd
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys

job_keywords = [
    "frontend",
    "backend",
    "html",
    "css",
    "javascript",
    "typescript",
    "aws",
    "cloud",
    "react",
    "testing",
    "java",
    ".net",
    "sass",
    "redux",
    "sql",
    "angular",
    "vue",
    "express",
    "node",
    "spring",
    "devops",
    "mongodb",
    "docker",
    "flask",
    "python",
    "graphql",
    "ci/cd",
]

timeout = 10
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
url = "https://www.glassdoor.co.uk/Job/fullstack-web-developer-jobs-SRCH_KO0,23.htm"
global browser
browser = webdriver.Chrome(options=chrome_options)
browser.get(url)


def click_stale_element(element: WebElement):
    checker = True
    while checker:
        try:
            element.click()
            checker = False
        except StaleElementReferenceException:
            checker = True


def locate_stale_element(element, driver, strategy: str, selector: str):
    checker = True
    while checker:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((strategy, selector))
            )
            checker = False
        except StaleElementReferenceException:
            print("-")
            checker = True
        except TimeoutException:
            checker = False

    return element.text if type(element) is WebElement else "NA"


def extract_job_details(job_cards: List["WebElement"], jobs_list: List):
    browser.implicitly_wait(10)
    for job_card in job_cards:
        click_stale_element(job_card)
        job_title = locate_stale_element(
            "",
            job_card,
            By.CSS_SELECTOR,
            '[data-test="job-link"]',
        )
        job_location = locate_stale_element(
            "",
            job_card,
            By.CSS_SELECTOR,
            '[data-test="emp-location"]',
        )

        job_salary = locate_stale_element(
            "",
            job_card,
            By.CSS_SELECTOR,
            'span[data-test="detailSalary"]',
        )

        job_description = locate_stale_element(
            "",
            browser,
            By.CLASS_NAME,
            "jobDescriptionContent",
        )
        # check if keyword exists in jd
        skills = []
        for keyword in job_keywords:
            if keyword in job_description.lower().replace(" ", ""):
                skills.append(keyword)

        job = {
            "title": job_title,
            "location": job_location,
            "salary": job_salary,
            "skills": skills,
        }
        jobs_list.append(job)


browser.find_elements(By.CLASS_NAME, "react-job-listing")[0].click()
browser.implicitly_wait(5)

modal_cancel = WebDriverWait(browser, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '[alt="Close"]'))
)
modal_cancel.click()

job_details: List = []
prev_button: WebElement = WebDriverWait(browser, timeout).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="pagination-prev"]'))
)
next_button: WebElement = WebDriverWait(browser, timeout).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="pagination-next"]'))
)
# keep running till the last page is reached
while next_button.is_enabled() or prev_button.is_enabled():
    job_cards = browser.find_elements(By.CLASS_NAME, "react-job-listing")
    extract_job_details(job_cards, job_details)
    click_stale_element(next_button)
    try:
        WebDriverWait(browser, timeout).until(EC.url_changes(browser.current_url))
    except TimeoutException:
        break

df = pd.DataFrame(data=job_details)
df.to_csv("dataset.csv")
print(df)
