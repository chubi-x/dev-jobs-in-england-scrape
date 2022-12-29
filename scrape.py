from re import search
from typing import Dict, List
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
browser = webdriver.Chrome(options=chrome_options)
jobs_list: List = []

glassdoor_data = dict(
    url="https://www.glassdoor.co.uk/Job/backend-jobs-SRCH_KO0,7.htm",
    job_list="react-job-listing",
    job_title=dict(by=By.CSS_SELECTOR, selector='[data-test="job-link"]'),
    job_description=dict(by=By.CLASS_NAME, selector="jobDescriptionContent"),
    job_salary=dict(by=By.CSS_SELECTOR, selector='span[data-test="detailSalary"]'),
    job_location=dict(by=By.CSS_SELECTOR, selector='[data-test="emp-location"]'),
    next_button=dict(by=By.CSS_SELECTOR, selector='[data-test="pagination-next"]'),
    prev_button=dict(by=By.CSS_SELECTOR, selector='[data-test="pagination-prev"]'),
)


def cancel_modal():
    browser.find_elements(By.CLASS_NAME, "react-job-listing")[0].click()
    try:
        modal_cancel = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[alt="Close"]'))
        )
        modal_cancel.click()
    except:
        pass


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
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((strategy, selector))
            )
            checker = False
        except StaleElementReferenceException:
            print("-")
            checker = True
        except TimeoutException:
            checker = False

    return element.text if type(element) is WebElement else "NA"


def extract_job_details(
    job_cards: List["WebElement"], jobs_list: List, site_details: Dict
):
    (
        job_title_details,
        job_description_details,
        job_salary_details,
        job_location_details,
    ) = [
        site_details[key]
        for key in (
            "job_title",
            "job_description",
            "job_salary",
            "job_location",
        )
    ]

    browser.implicitly_wait(10)
    for job_card in job_cards:
        click_stale_element(job_card)
        job_title = locate_stale_element(
            "", job_card, job_title_details["by"], job_title_details["selector"]
        )
        job_location = locate_stale_element(
            "", job_card, job_location_details["by"], job_location_details["selector"]
        )

        job_salary = locate_stale_element(
            "", job_card, job_salary_details["by"], job_salary_details["selector"]
        )

        job_description = locate_stale_element(
            "",
            browser,
            job_description_details["by"],
            job_description_details["selector"],
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


def scrape_pages(site_details):
    (url, job_list, prev_button_details, next_button_details,) = [
        site_details[key]
        for key in (
            "url",
            "job_list",
            "prev_button",
            "next_button",
        )
    ]
    browser.get(url)
    cancel_modal()

    prev_button: WebElement = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located(
            (prev_button_details["by"], prev_button_details["selector"])
        )
    )
    next_button: WebElement = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located(
            (next_button_details["by"], next_button_details["selector"])
        )
    )
    # keep running till the last page is reached
    while next_button.is_enabled() or prev_button.is_enabled():
        job_cards = browser.find_elements(By.CLASS_NAME, job_list)
        extract_job_details(job_cards, jobs_list, site_details)
        # click_stale_element(next_button)
        try:
            WebDriverWait(browser, timeout).until(EC.url_changes(browser.current_url))
        except TimeoutException:
            break
    browser.quit()


scrape_pages(glassdoor_data)

df = pd.DataFrame(data=jobs_list)
df.to_csv("dataset.csv", mode="a", header=False)
