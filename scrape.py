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

from site_data import glassdoor_data
from site_data import indeed_data

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


def cancel_single_modal(by: str, selector: str):
    try:
        modal_cancel = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((by, selector))
        )
        modal_cancel.click()
    except:
        pass


def cancel_indeed_modals(site_details):
    if "indeed" in site_details["url"]:
        modal_list = [site_details[key] for key in ("cancel_google", "cancel_modal")]
        for modal in modal_list:
            cancel_single_modal(modal["by"], modal["selector"])
            print("canceled", modal)


def cancel_modals(site_details: Dict):
    first_item = browser.find_elements(By.CLASS_NAME, site_details["job_list"])[0]
    browser.execute_script("arguments[0].click()", first_item)

    if "indeed" in site_details["url"]:
        cancel_single_modal(
            site_details["cancel_cookies"]["by"],
            site_details["cancel_cookies"]["selector"],
        )

    else:
        cancel_single_modal(
            site_details["cancel_modal"]["by"],
            site_details["cancel_modal"]["selector"],
        )


def click_stale_element(element):
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

    # browser.implicitly_wait(10)
    for job_card in job_cards:
        click_stale_element(job_card)
        browser.implicitly_wait(10)
        if job_cards.index(job_card) == 0:
            cancel_indeed_modals(site_details)

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


def find_paginators(prev_button_details, next_button_details):
    prev_present = False
    next_present = False
    prev_button = None
    next_button = None

    try:
        prev_button = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (prev_button_details["by"], prev_button_details["selector"])
            )
        )
        prev_present = True
    except TimeoutException:
        pass

    try:
        next_button = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (next_button_details["by"], next_button_details["selector"])
            )
        )
        next_present = True
    except TimeoutException:
        pass

    return prev_present, next_present, prev_button, next_button


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
    browser.implicitly_wait(10)
    cancel_modals(site_details)

    # keep running till the last page is reached
    while True:
        prev_present, next_present, prev_button, next_button = find_paginators(
            prev_button_details, next_button_details
        )
        print("found paginators")
        if (prev_present and next_present) or (type(next_button) is WebElement):
            print("next present:", next_present, "\n prev present:", prev_present)
            job_cards = browser.find_elements(By.CLASS_NAME, job_list)
            print("extracting jobs...")
            extract_job_details(job_cards, jobs_list, site_details)
            print("extracted jobs")
            click_stale_element(next_button)
            browser.implicitly_wait(10)

            cancel_indeed_modals(site_details)
            print("next clicked")
            if "glassdoor" in site_details["url"]:
                try:
                    print("checking if there is next page")
                    WebDriverWait(browser, timeout).until(
                        EC.url_changes(browser.current_url)
                    )
                    print("there is a next page")
                except:
                    "no next page"
                    break
        else:
            print("not satisfied")
            break
    print("broken out of loop")
    browser.quit()


scrape_pages(indeed_data)

df = pd.DataFrame(data=jobs_list)
df.to_csv("dataset.csv", mode="a", header=False)
print(df)
