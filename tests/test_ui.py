"""Run: APP_URL=http://ALB_DNS python tests/test_ui.py"""

import os
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


url = os.environ.get("APP_URL", "http://localhost:8080").rstrip("/")
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
try:
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    heading = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1")))
    assert heading.text == "Taskboard", f"Unexpected heading: {heading.text!r}"

    title = f"Selenium check {uuid.uuid4().hex[:8]}"
    driver.find_element(By.ID, "task-title").send_keys(title)
    driver.find_element(By.CSS_SELECTOR, "#add-form button[type=submit]").click()
    wait.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#task-list li:first-child .task-title"), title
        )
    )
    assert driver.find_element(By.CSS_SELECTOR, "#task-list li:first-child .task-title").text == title
    driver.save_screenshot("selenium-pass.png")
    print(f"PASS: heading and newly created task verified at {url}; screenshot: selenium-pass.png")
finally:
    driver.quit()
