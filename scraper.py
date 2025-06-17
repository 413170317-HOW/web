# scraper.py
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def init_driver():
    options = webdriver.EdgeOptions()
    options.add_argument('disable-gpu')
    options.add_argument('window-size=500,1080')
    return webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

def wait_for_page_load(driver):
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

def get_cert_links(driver):
    ul_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="content-browser-container"]/div/div/div[2]/ul'))
    )
    li_elements = ul_element.find_elements(By.XPATH, './li/article/div[1]/a')
    return [link.get_attribute("href") for link in li_elements]

# 模組
def click_modules(driver):
    titles = []
    try:
        links = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "column") and contains(@class, "is-auto") and contains(@class, "padding-none")]//a'))
        )
        for link in links:
            text = link.text.strip()
            if text:
                print(f"        🔗 模組：{text}")
                titles.append(text)
    except Exception as e:
        print(f"        ⚠️ 模組擷取失敗：{e}")
    return titles

# 課程 
def process_courses(driver, db, cert_title, cert_url):
    try:
        links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//section[6]//ul/li/article/div[2]/ul[2]//a'))
        )

        for idx, link in enumerate(links, start=1):
            course_title = link.text.strip()
            course_url = link.get_attribute("href")
            print(f"    👉 課程 {idx}：{course_title} ({course_url})")

            driver.execute_script("window.open(arguments[0]);", course_url)
            driver.switch_to.window(driver.window_handles[-1])
            wait_for_page_load(driver)

            modules = click_modules(driver)

            #for module_title in modules:
                #db.insert_course(cert_url, course_title, course_url, module_title)

            db.insert_course_structure(
                certification_title=cert_title,
                certification_url=cert_url,
                course_title=course_title,
                course_url=course_url,
                module_titles=modules
            )

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

    except Exception as e:
        print(f"    ❌ 課程處理失敗：{e}")
