# 3중 for문 개선 -> formdata를 웹 페이지에서 수집해서 동적으로 적용해야함
import requests
import time
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYLOAD_FILE = os.path.join(PROJECT_ROOT, "etc", "A03_sqli_payload.txt")  # SQLi 페이로드 파일 경로

success_results = []

def read_lines_file():
    with open(PAYLOAD_FILE, "r") as file:
        return file.read().splitlines()

def is_time_based(duration):
    print(duration)
    return duration >= 5

# 수정된 요청 함수: 한 endpoint에 대해 한 번 요청만 함
def send_request(full_url, data, method):
    try:
        print(f"[+] 요청 URL: {full_url}")
        start = time.time()
        if method.upper() == "POST":
            response = requests.post(full_url, data=data)
        else:
            response = requests.get(full_url, params=data)
        end = time.time()
        duration = end - start
        return response, duration
    except requests.RequestException as e:
        print(f"[!] 요청 실패: {e}, {method}, {data}")
        return None, None

# 메인 테스트 함수
def start_sqli(obj_list):
    # print(f"[*] SQLi 테스트 시작: {url}\n")
    # url = "http://172.16.100.180"
    # login_path = "/index.php?controller=authentication&back=my-account"
    # login_data = {
    #     "email":"jhjh@naver.com",
    #     "passwd":"jjhjjh",
    #     "SubmitLogin":"Authentication"
    # }
    
    # login_path = ""
    # login_data = {}
    
    # url = "http://testphp.vulnweb.com"
    # login_path = "/userinfo.php"
    # login_data = {
    #     "uname" : "test",
    #     "pass" : "test"
    # }

    # obj_list = start_crawl(url, login_path, login_data)
    
    payloads = read_lines_file() # 저장된 payload 저장

    for obj in obj_list:
        formlist = obj.formData #list 저장되어있음
        path = obj.path
        for formdata in formlist:  #form 태그별 안에 있는 input 태그와 method 저장장
            method = formdata['method']
            action = formdata['action']
            inputs = formdata['inputs']

            
            # print(inputs.values())
            if "payload" not in inputs.values():
                # print(f"[!] {action}에 payload가 없습니다. 스킵합니다.")
                continue
            
            for payload in payloads:
                data = {}
                for key, val in inputs.items():
                    if val == 'payload' or val == '':
                        data[key] = payload
                    else:
                        data[key] = val
                
                print("action : ", action)
                response, duration = send_request(action, data, method)
                

                findings = []
                if "sql" in response.text.lower() or "syntax" in response.text.lower():
                    findings.append(f"⚠️ SQL 오류 메시지 발견 (Error-based)")
                if is_time_based(duration):
                    findings.append(f"⏱️ 응답 지연 {round(duration,2)}초 (Time-based)")
                if response.status_code == 500:
                    findings.append(f"⚠️ 서버 500 에러")
                if ("Welcome" in response.text or "Dashboard" in response.text) and "login" in path:
                    findings.append(f"✅ 로그인 우회 또는 결과 조작 가능성")

                if findings:
                    result = {
                        "url": path,
                        "data": data,
                        "method" : method,
                        "duration": round(duration, 2),
                        "findings": findings
                    }
                    success_results.append(result)

            print("-" * 50)

    print("\n\n=== 테스트 결과 요약 ===")
    for idx, result in enumerate(success_results,1):
        time.sleep(0.5)
        print("=" * 60)
        print(f"[#{idx}] SQL Injection 검사 결과")
        print(f"[URL     ] {result['url']}")
        print(f"[METHOD  ] {result['method']}")
        print(f"[DATA    ] {result['data']}")
        print(f"[TIME    ] {result['duration']:.3f}초")

        if result["findings"]:
            print("[FINDINGS]")
            for finding in result["findings"]:
                print(f"  └─ {finding}")
        else:
            print("[FINDINGS] 없음")

        print("=" * 60)
        
    for idx2, result in enumerate(success_results, 1):
        filename = f"sqli/{idx2}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("=" * 60 + "\n")
            file.write(f"[#{idx2}] SQL Injection 검사 결과\n")
            file.write(f"[URL     ] {result['url']}\n")
            file.write(f"[METHOD  ] {result['method']}\n")
            file.write(f"[DATA    ] {result['data']}\n")
            file.write(f"[TIME    ] {result['duration']:.3f}초\n")

            if result["findings"]:
                file.write("[FINDINGS]\n")
                for finding in result["findings"]:
                    file.write(f"  └─ {finding}\n")
            else:
                file.write("[FINDINGS] 없음\n")

            file.write("=" * 60 + "\n")         
                        

# def test_sqli():    
#     from crawl import start_crawl
    
#     url = "http://testphp.vulnweb.com"
#     login_path = "/userinfo.php"
#     login_data = {
#         "uname" : "test",
#         "pass" : "test"
#     }
    
#     obj_list = start_crawl(url, login_path, login_data)
    
#     start_sqli(obj_list)
    
# test_sqli()