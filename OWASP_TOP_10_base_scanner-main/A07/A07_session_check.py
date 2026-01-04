# 설명 : 초기에 로그인한 세션을 가지고 세션 하이재킹이 가능한지 확인하는 코드
# 필수 데이터 : 로그인 URL, 로그아웃 URL, 로그인 체크 URL, 로        

from requests.utils import requote_uri
import requests
import datetime
import json
# import os

# def print_banner(title):
#     """결과를 시각적으로 구분하는 배너 출력"""
#     print("=" * 60)
#     print(f"  {title}")
#     print("=" * 60)


# def log_result(result, details):
#     """결과를 파일에 로그 저장"""
#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     log_entry = {
#         "timestamp": timestamp,
#         "test_type": "세션 하이재킹 테스트",
#         "result": result,
#         "details": details
#     }
    
#      로그 디렉토리 생성
#     os.makedirs("../logs", exist_ok=True)
    
#     로그 파일에 저장
#     with open("../logs/session_hijack_test.log", "a", encoding="utf-8") as f:
#         f.write(f"{json.dumps(log_entry, ensure_ascii=False, indent=2)}\n")


class Session_Hijacking():

    def session_expiration(self,session_cookie,logout_url, login_check_url):
        """세션 만료 기능 확인"""
        try:
            resp = requests.get(logout_url, allow_redirects=False, timeout=10)
            if resp.status_code == 200 or resp.status_code == 302:
                resp = requests.get(login_check_url, allow_redirects=False, cookies=session_cookie, timeout=10)
                if resp.status_code == 200:
                    print("🔴 세션 만료 실패 - 세션이 여전히 유효함")
                    print("📝 상세 정보:")
                    print(f"   - 상태 코드: {resp.status_code}")
                    print(f"   - 테스트 URL: {login_check_url}")
                    print(f"   - 사용된 쿠키: {', '.join(session_cookie.keys())}")
                    print(f"   - 응답 크기: {len(resp.content)} bytes")
                    
        
                    return False
                elif resp.status_code == 302 or resp.status_code == 301:
                    print("✅ 세션 만료 성공 - 세션이 무효화됨")
                    return True
            else:
                print(f"❌ 로그아웃 실패 - 상태 코드: {resp.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ 네트워크 오류: {str(e)}")
            return False
        
    def parse_scan_result(self, results): 
        """스캔 결과를 파싱하여 테스트 항목 생성"""
        details = []

        try:
            if(results):
                details.append(
                    {
                        "cookies_used": results["cookies_used"],
                        "description": f"Status Code: {results['status_code']}, URL: {results['url']}, Response Size: {results['response_size']} bytes",                
                    }
                )
        except KeyError as e:
            print(f"❌ 결과 파싱 오류: 예상치 못한 결과 형식 : {e}")

        return details

    def session_hijack_check(self, session_cookie, login_check_url):
        """세션 하이재킹 가능성 확인"""
        try:
            login_check_url = requote_uri(login_check_url)
            resp = requests.get(login_check_url, allow_redirects=False, cookies=session_cookie, timeout=10)
            
            result_details = {
                "status_code": resp.status_code,
                "url": login_check_url,
                "cookies_used": list(session_cookie.keys()),
                "response_size": len(resp.content)
            }

            print(f"{login_check_url} 에 대한 응답 상태 코드: {resp.status_code}, cookies : {session_cookie}")

            if resp.status_code == 200:
                # 로그인 상태 확인을 위한 추가 검증
                    # print_banner("⚠️  보안 취약점 발견!")
                print("🔴 세션 하이재킹 가능")
                print("📝 상세 정보:")
                print(f"   - 상태 코드: {resp.status_code}")
                print(f"   - 테스트 URL: {login_check_url}")
                print(f"   - 사용된 쿠키: {', '.join(session_cookie.keys())}")
                print(f"   - 응답 크기: {len(resp.content)} bytes")
                    # print("\n🛡️  권장 조치:")
                    # print("   1. 세션 타임아웃 설정 강화")
                    # print("   2. 세션 ID 재생성 구현")
                    # print("   3. HttpOnly, Secure 쿠키 플래그 설정")
                    # print("   4. CSRF 토큰 검증 강화")
                    
                    # log_result("VULNERABLE", result_details)
                return result_details                
            elif resp.status_code == 302 or resp.status_code == 301:
                # print_banner("✅ 보안 정상")
                print("🟢 세션 하이재킹 불가능 (리다이렉트 발생)")
                print(f"   - 리다이렉트 위치: {resp.headers.get('Location', 'Unknown')}")
                # log_result("SECURE", result_details)
                # return False                
            else:
                # print_banner("❓ 예상치 못한 응답")
                print(f"🟡 상태 코드: {resp.status_code}")
                print("   - 추가 분석이 필요합니다.")
                # log_result("UNKNOWN", result_details)
                # return None
            
            return {}
                
        except requests.RequestException as e:
            # print_banner("❌ 테스트 실행 오류")
            print(f"🔴 오류: {str(e)}")
            # log_result("ERROR", {"error": str(e), "url": login_check_url})
            return {}
    
    def run(self, config):
        """세션 하이재킹 테스트 실행"""
        details = []

        login_url = config.get("login_url", "")
        login_check_url = config.get("web_url", "") + "my-account"
        test_email = config.get("test_email", "")
        test_password = config.get("test_password", "")

        session = requests.Session()
        login_format = {
            "email": test_email,
            "password": test_password,
            "submitLogin": "1"
            }

        try:
            print("🔄 로그인 시도 중...")
            resp = session.post(login_url, data=login_format, timeout=10)
            
            if resp.status_code == 200 or resp.status_code == 302:
                session_cookie = session.cookies.get_dict()
                
                if session_cookie:
                    print(f"✅ 로그인 성공 - 쿠키 획득: {list(session_cookie.keys())}")
                    # print("\n🔍 세션 하이재킹 테스트 진행 중...")
                    
                    # 세션 하이재킹 테스트 실행
                    session_hijack_result = self.session_hijack_check(session_cookie, login_check_url)



                    details = self.parse_scan_result(session_hijack_result)
                    
                else:
                    print("❌ 로그인 실패 - 세션 쿠키를 획득하지 못했습니다.")
                    
            else:
                print(f"❌ 로그인 실패 - 상태 코드: {resp.status_code}")
            
        except requests.RequestException as e:
            print(f"❌ 네트워크 오류: {str(e)}")

        return details
        
        
# def main():
#     """메인 실행 함수"""
#     # print_banner("세션 하이재킹 취약점 테스트 시작")
    
#     # 설정 파일에서 정보 로드
#     try:
#         with open("../etc/user_information.json", "r", encoding="utf-8") as f:
#             config = json.load(f)
            
#         login_url = config.get("login_url", "")
#         login_check_url = config.get("web_url", "") + "/my-account"
#         test_email = config.get("test_email", "")
#         test_password = config.get("test_password", "")
        
#     except FileNotFoundError:
#         print("❌ 설정 파일을 찾을 수 없습니다: ../etc/user_information.json")
#         return
#     except json.JSONDecodeError:
#         print("❌ 설정 파일 형식이 올바르지 않습니다.")
#         return
    
#     session = requests.Session()
    
#     login_format = {
#         "email": test_email,
#         "password": test_password,
#         "submitLogin": "1"
#     }
    
#     try:
#         print("🔄 로그인 시도 중...")
#         resp = session.post(login_url, data=login_format, timeout=10)
        
#         if resp.status_code == 200 or resp.status_code == 302:
#             session_cookie = session.cookies.get_dict()
            
#             if session_cookie:
#                 print(f"✅ 로그인 성공 - 쿠키 획득: {list(session_cookie.keys())}")
#                 # print("\n🔍 세션 하이재킹 테스트 진행 중...")
                
#                 # 세션 하이재킹 테스트 실행
#                 sesssion_hijack_result = session_hijack_check(session_cookie, login_check_url)
#                 Session_Expiration_result = Session_Expiration(session_cookie,login_url, login_check_url)
#                 # 최종 결과 요약
#                 # print_banner("테스트 완료")
#                 # if result is True:
#                 #     print("🚨 경고: 이 웹사이트는 세션 하이재킹에 취약합니다!")
#                 # elif result is False:
#                 #     print("✅ 양호: 세션 보안이 적절히 구현되어 있습니다.")
#                 # else:
#                 #     print("❓ 결과 불명확: 수동 검토가 필요합니다.")
                    
#                 print(f"\n📋 상세 로그는 ../logs/session_hijack_test.log 파일에서 확인하세요.")
                
#             else:
#                 print("❌ 로그인 실패 - 세션 쿠키를 획득하지 못했습니다.")
                
#         else:
#             print(f"❌ 로그인 실패 - 상태 코드: {resp.status_code}")
            
#     except requests.RequestException as e:
#         print(f"❌ 네트워크 오류: {str(e)}")

if __name__ == "__main__":
    
    with open("../etc/user_info.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    obj = Session_Hijacking()
    result = obj.run(config)

    with open("session_hijack_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)