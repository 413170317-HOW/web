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
    """ 
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
    """
    modules_data = []

    try:
        module_blocks = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-bi-name="module"]'))
        )

        for idx, module in enumerate(module_blocks, start=1):
            print(f"🔗 第 {idx} 個模組：")

            try:
                link_elem = module.find_element(By.CSS_SELECTOR, 'a.font-weight-semibold')
                link_text = link_elem.text.strip()
                link_href = link_elem.get_attribute('href')

                try:
                    summary_div = module.find_element(By.CSS_SELECTOR, '.module-summary')
                    desc_text = summary_div.get_attribute('textContent').strip()
                except Exception as e:
                    desc_text = "(❌ 無法取得敘述)"

                print(f"    🌐 連結：{link_href}")
                print(f"    📘 標題：{link_text}")
                print(f"    📝 敘述：{desc_text}")

                modules_data.append({
                    'title': link_text,
                    'url': link_href,
                    'description': desc_text
                })

            except Exception as e:
                print(f"⚠️ 第 {idx} 個模組擷取失敗：{e}")
    except Exception as e:
        print(f"⚠️ 模組區塊擷取失敗：{e}")
    return modules_data


# 課程 
def process_courses(driver, db, cert_title, cert_url):
    try:
        course_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//section[6]//ul/li/article/div[2]/ul[2]//a'))
        )
        try:
                description_element = driver.find_element(By.XPATH, '//*[@id="certification-hero"]/div/div[2]/p[2]')
                course_description = description_element.text.strip()
        except:
                course_description = "（找不到介紹）"
        print(f"   認證介紹：{course_description}")

        for idx, link in enumerate(course_links, start=1):
            course_title = link.text.strip()
            course_url = link.get_attribute("href")
            print(f"    👉 課程 {idx}：{course_title} ({course_url})")

            driver.execute_script("window.open(arguments[0]);", course_url)
            driver.switch_to.window(driver.window_handles[-1])
            wait_for_page_load(driver)

            # 爬課程介紹
            course_description = "（找不到課程介紹）"
            for i in [4, 5, 6]:
                try:
                    xpath = f'//*[@id="main"]/div[3]/div[1]/div/div/div/div/div[{i}]/p'
                    description_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    course_description = description_element.text.strip()
                    break  # 找到了就退出迴圈
                except:
                    continue
            print(f"      課程介紹：{course_description}")

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