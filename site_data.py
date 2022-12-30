from selenium.webdriver.common.by import By

glassdoor_data = dict(
    url="https://www.glassdoor.co.uk/Job/fullstack-web-developer-jobs-SRCH_KO0,23.htm",
    cancel_modal=dict(by=By.CSS_SELECTOR, selector='[alt="Close"]'),
    job_list="react-job-listing",
    job_title=dict(by=By.CSS_SELECTOR, selector='[data-test="job-link"]'),
    job_description=dict(by=By.CLASS_NAME, selector="jobDescriptionContent"),
    job_salary=dict(by=By.CSS_SELECTOR, selector='span[data-test="detailSalary"]'),
    job_location=dict(by=By.CSS_SELECTOR, selector='[data-test="emp-location"]'),
    next_button=dict(by=By.CSS_SELECTOR, selector='[data-test="pagination-next"]'),
    prev_button=dict(by=By.CSS_SELECTOR, selector='[data-test="pagination-prev"]'),
)

indeed_data = dict(
    url="https://uk.indeed.com/jobs?q=fullstack+developer&l=United+Kingdom",
    cancel_cookies=dict(by=By.ID, selector="onetrust-reject-all-handler"),
    cancel_google=dict(by=By.CLASS_NAME, selector="icl-Card-close"),
    cancel_modal=dict(by=By.CLASS_NAME, selector="icl-Modal-close"),
    job_list="slider_item",
    job_title=dict(by=By.CLASS_NAME, selector="jobTitle"),
    job_description=dict(by=By.ID, selector="jobDescriptionText"),
    job_salary=dict(by=By.CLASS_NAME, selector="salary-snippet-container"),
    job_location=dict(by=By.CLASS_NAME, selector="companyLocation"),
    next_button=dict(
        by=By.CSS_SELECTOR, selector='[data-testid="pagination-page-next"]'
    ),
    prev_button=dict(
        by=By.CSS_SELECTOR, selector='[data-testid="pagination-page-prev"]'
    ),
)
