#스레드를 통해 속도 향상
# 스레드 : 각 엔드포인트별로 payload 를 삽입하여 XSS 공격을 시도하는 함수

import requests
import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException
import urllib.parse
import time 
from datetime import datetime
from os import path, makedirs

PROJECT_ROOT = path.dirname(path.dirname(path.abspath(__file__)))
XSS_PAYLOAD_PATH = path.join(PROJECT_ROOT, "etc", "A03_xss_payload.txt")
MAX_THREAD = 5


def read_lines_file():
    with open(XSS_PAYLOAD_PATH, "r") as file:
        return file.read().splitlines()

def check_alert(url, data, method):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(1)
    try:
        if method.upper() == 'GET':
            full_url = url + "?" + urllib.parse.urlencode(data)
            driver.get(full_url)
        elif method.upper() == 'POST':
            driver.get("about:blank")
            script = """
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = arguments[0];
            for (var key in arguments[1]) {
                var input = document.createElement('input');
                input.name = key;
                input.value = arguments[1][key];
                form.appendChild(input);
            }
            document.body.appendChild(form);
            form.submit();
            """
            driver.execute_script(script, url, data)
        time.sleep(2)
        try:
            driver.switch_to.alert
            driver.quit()
            return True
        except NoAlertPresentException:
            driver.quit()
            return False
    except Exception:
        driver.quit()
        return False

def scan_form_for_xss(path, formdata, payloads, success_results, semaphore, thread_id):
    with semaphore:
        method = formdata['method']
        action = formdata['action']
        inputs = formdata['inputs']

        print(f"\n[+]{thread_id} {action}, {method} 에 대해 XSS 스캔을 시작합니다...")

        for payload in payloads[:5]:
            data = {}

            if "payload" not in inputs.values():
                # print(inputs)
                break

            for key, val in inputs.items():
                if val == 'payload' or val == '':
                    data[key] = payload
                else:
                    data[key] = val

            try:
                if check_alert(action, data, method):
                    # print("xss!!!")
                    # print("payload : ", payload)
                    result = {
                        "url": path,
                        "data": data,
                        "method": method
                    }
                    success_results.append(result)
                    break
                else:
                    # print(f"[-]{thread_id} 필드 '{path}, {data}'에서는 페이로드가 반영되지 않음.")
                    continue
            except requests.RequestException as e:
                print(f"[!] 요청 실패: {e}, {method}, {data}")
                exit(-1)

def start_xss(obj_list):
    success_results = []
    payloads = read_lines_file()
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = f"xss/{now_str}"
    makedirs(result_dir, exist_ok=True)

    threads = []
    thread_id = 1
    semaphore = threading.Semaphore(MAX_THREAD)  # 최대 5개 동시 실행

    for idx1, obj in enumerate(obj_list, 1):
        formlist = obj.formData
        path = obj.path
        
        for formdata in formlist:
            t = threading.Thread(
                target=scan_form_for_xss,
                args=(path, formdata, payloads, success_results, semaphore, thread_id)
            )
            t.start()
            thread_id += 1
            threads.append(t)

    for t in threads:
        t.join()

    for idx2, result in enumerate(success_results, 1):
        filename = f"{result_dir}/{idx2}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("=" * 60 + "\n")
            file.write(f"[#{idx2}] XSS 검사 결과\n")
            file.write(f"[URL     ] {result['url']}\n")
            file.write(f"[METHOD  ] {result['method']}\n")
            file.write(f"[DATA    ] {result['data']}\n")
            file.write("=" * 60 + "\n")       


# def test_xss():
#     from crawl import start_crawl

#     url = "http://testasp.vulnweb.com/"
#     login_path = "/userinfo.php"
#     login_data = {
#         "uname" : "test",
#         "pass" : "test"
#     }
    
#     obj_list = start_crawl(url, login_path, login_data)
#     start_xss(obj_list)

# test_xss()