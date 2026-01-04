import re
import datetime
import ipaddress
import logging
import json
import os
import pymysql

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(PROJECT_ROOT, "logs", "A02_check_cryptographic.log")

# logs 디렉토리 생성 (없으면)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


# def load_config():
#     try:
#         with open(DB_INFO, 'r') as f:
#             info = json.load(f)
#         config ={
#         "host": info["host"],
#         "user": info["DB_ID"],
#         "password": info["DB_PW"],
#         "database": info["DB_NAME"],
#         "charset": "utf8mb4"
#         }
        
#         return config
    
#     except FileNotFoundError:
#         print("config.json 파일이 없습니다. 기본 설정을 사용합니다.")
#         exit(-1)

class CheckCryptographic:
    HASH_PATTERNS = {
        'md5': r"\bmd5\s*\(",
        'sha1': r"\bsha1\s*\(",
        'md4': r"\bmd4\s*\(",
        'md2': r"\bmd2\s*\(",
        'crc32': r"\bcrc32\s*\(",
        'des': r"\bdes\s*\(",
        'rc4': r"\brc4\s*\("
    }
    def __init__(self):
        self.KEYWORD_FILE = os.path.join(PROJECT_ROOT, "etc", "A02_crytogaphic_keywords.txt")
        self.all_found_vulnerabilities = set()  # 중복 제거를 위해 set 사용


    def parse_scan_results(self, results):
        """스캔 결과를 파싱하여 취약점 리스트에 추가하는 함수"""
        details = []
        for i, result in enumerate(results, 1):
            details.append({
                "file": result.get("filename", 'Unknown'),
                "description": f"Weak hash algorithm '{result.get('hash', 'Unknown')}' detected.",
                "lines": result.get("lines", [])            
            })

        return details

    def read_keywords_from_file(self):
        """민감 키워드 파일을 읽어 리스트로 반환하는 함수"""
        try:
            with open(self.KEYWORD_FILE, 'r') as f:
                keywords = [line.strip() for line in f if line.strip()]
            return keywords
        except FileNotFoundError:
            print("sensitive_keywords.txt 파일이 없습니다. 기본 키워드를 사용합니다.")
            logging.error("sensitive_keywords.txt 파일이 없습니다.")            


    def find_hash_in_code(self, code: str, filename) -> list[dict]:
        """코드 내에서 해시 패턴을 찾아 반환하는 함수"""

        vulnerability_hash = []  # 초기화

        for hash_name, pattern in self.HASH_PATTERNS.items():
            line_nums = []
            if re.search(pattern, code, re.IGNORECASE):
                self.all_found_vulnerabilities.add(hash_name)  # 전체 리스트에 추가
                print(f"\n🔴 Found vulnerable hash '{hash_name}' in file: {filename}")

                    # 각 줄을 검사해서 정확한 위치 찾기 (주석 제외)
                for line_num, line in enumerate(code.splitlines(), 1):
                        # 주석 처리된 줄 건너뛰기
                        stripped_line = line.strip()
                        if (stripped_line.startswith('//') or 
                            stripped_line.startswith('#') or 
                            stripped_line.startswith('/*') or
                            stripped_line.startswith('*') or
                            stripped_line.startswith('<!--')):
                            continue
                        
                        # 여러 줄 주석 내부인지 확인 (/* ... */ 블록)
                        if '/*' in line and '*/' in line:
                            before_comment = line.split('/*')[0]
                            after_comment = line.split('*/')[-1] if '*/' in line else ''
                            line_to_check = before_comment + after_comment
                        else:
                            line_to_check = line
                        
                        if re.search(pattern, line_to_check, re.IGNORECASE):
                            print(f"  📍 Line {line_num}: {line.strip()}")
                            line_nums.append(line_num)

                vulnerability_hash.append(
                    {
                        "filename": filename,
                        "hash": hash_name,
                        "pattern": pattern,
                        "lines": line_nums
                    }
                )

        return vulnerability_hash

    # {
    #   "path": "/home/ruqos/Desktop/project/PrestaShop/js/jquery/plugins/jstree/themes/index.php",
    #   "language": "PHP",
    #   "content": "<?php\n/**\n * 2007-2020 PrestaShop SA and Contributors\n *\n * NOTICE OF LICENSE\n *\n * This source file is subject to the Open Software License (OSL 3.0)\n * that is bundled with this package in the file LICENSE.txt.\n * It is also available through the world-wide-web at this URL:\n * https://opensource.org/licenses/OSL-3.0\n * If you did not receive a copy of the license and are unable to\n * obtain it through the world-wide-web, please send an email\n * to license@prestashop.com so we can send you a copy immediately.\n *\n * DISCLAIMER\n *\n * Do not edit or add to this file if you wish to upgrade PrestaShop to newer\n * versions in the future. If you wish to customize PrestaShop for your\n * needs please refer to https://www.prestashop.com for more information.\n *\n * @author    PrestaShop SA <contact@prestashop.com>\n * @copyright 2007-2020 PrestaShop SA and Contributors\n * @license   https://opensource.org/licenses/OSL-3.0 Open Software License (OSL 3.0)\n * International Registered Trademark & Property of PrestaShop SA\n */\n\nheader(\"Expires: Mon, 26 Jul 1997 05:00:00 GMT\");\nheader(\"Last-Modified: \".gmdate(\"D, d M Y H:i:s\").\" GMT\");\n\nheader(\"Cache-Control: no-store, no-cache, must-revalidate\");\nheader(\"Cache-Control: post-check=0, pre-check=0\", false);\nheader(\"Pragma: no-cache\");\n\nheader(\"Location: ../\");\nexit;\n"
    # }

    def scan_file_for_hashes(self, source_files: str) -> list[str]:
        """파일에서 해시 패턴을 찾아 반환하는 함수"""
        print("scan_file_for_hashes")
        vulnerability_files = []  # 초기화 
        
        for source in source_files:
            code = source.get("content", "")
            filename = source.get("path", "Unknown file")

            vulnerability_files.extend(self.find_hash_in_code(code, filename))

        return vulnerability_files

    def get_weak_encryption_type(self, value: str) -> str | None:
        """주어진 값이 약한 암호화 알고리즘인지 검사하는 함수."""
        if not value or not isinstance(value, str):
            return None

        value = value.strip()
        weak_patterns = {
            "MD5": r"^[a-fA-F0-9]{32}$",
            "SHA-1": r"^[a-fA-F0-9]{40}$",
            "NTLM": r"^\$NT\$[A-F0-9]{32}$",
            "Base64": r"^[A-Za-z0-9+/=]{16,}$",
            "Possibly DES/RC4 (Hex)": r"^[a-fA-F0-9]{16}$",
        }

        for name, pattern in weak_patterns.items():
            if re.fullmatch(pattern, value):
                return name  # 해당하는 알고리즘 이름 반환

        return None  # 아무 패턴에도 해당하지 않음



    def select_table_column_name(self,cursor, sensitive_keywords, database):
        """민감 키워드를 포함하는 테이블과 컬럼 이름을 조회하는 함수"""

        like_conditions = ' OR '.join([f"column_name LIKE '%%{kw}%%'" for kw in sensitive_keywords])
        query = f"""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = %s
            AND ({like_conditions})
        """
        cursor.execute(query, database)
        return [(row[0], row[1]) for row in cursor.fetchall()]

    


    def is_plaintext(self, value) -> bool:
        """평문인지 검사하는 함수"""
        _short_readable_pattern = re.compile(r"^[A-Za-z0-9\s.,!@#%^&*()\-_=+<>?:\"';\[\]{}|\\/~`ㄱ-ㅎ가-힣]+$")
        _contains_space_or_at = re.compile(r"[\s@]")
        
        # None → 평문
        if value is None:
            return True

        # datetime → 암호화 아님 (시스템 값)
        if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
            return True

        # 문자열이 아닌 경우 → 평문으로 간주
        if not isinstance(value, str):
            return True

        value = value.strip()
        if not value:
            return True  # 빈 문자열은 평문

        # IP 주소인지 검사
        if 7 <= len(value) <= 45:  # IPv4 ~ IPv6 최대 길이
            try:
                ipaddress.ip_address(value)
                return True  # IP 주소는 평문으로 간주
            except ValueError:
                pass  # IP가 아니면 계속 검사

        # 평문 패턴 검사
        if len(value) <= 20 and _short_readable_pattern.fullmatch(value):
            return True
        if _contains_space_or_at.search(value):
            return True

        return False

    # 자동 검사 실행
    def run(self, source_files):
        # config = load_config()


        scan_results = self.scan_file_for_hashes(source_files)

        details = self.parse_scan_results(scan_results)

        return details
        # return self.vulnerability_files
    
        # config = {
        #     "host": config["host"],
        #     "user": config["DB_ID"],
        #     "password": config["DB_PW"],
        #     "database": config["DB_NAME"],
        #     "charset": "utf8mb4"
        # }
        
        # conn = pymysql.connect(**config)
        # cursor = conn.cursor()

        # sensitive_keywords = self.read_keywords_from_file()
        # if not sensitive_keywords:
        #     sensitive_keywords = ['password', 'passwd', 'pass', 'pwd', 'secret', 'token', 'auth', 'key', 'hash', 'credential']
        #     logging.warning("민감 키워드 파일을 읽지 못해 기본 키워드를 사용합니다.")

        # # 1. 암호 관련 컬럼 자동 탐색
        # targets = self.select_table_column_name(cursor, sensitive_keywords, config['database'])


        # print(f"\n총 {len(targets)}개의 민감정보 컬럼 후보가 발견되었습니다.\n")

        # # 2. 각 테이블/컬럼에서 데이터 추출 및 해시 타입 판별
        # for table, column in targets:
        #     try:
        #         query = "SELECT `{column}` FROM `{table}` LIMIT 5"
        #         cursor.execute(query)
        #         rows = cursor.fetchall()

        #         for row in rows:
                    
        #             if self.is_plaintext(row[0]):
        #                 {
        #                     "table": table,
        #                     "column": column,
        #                     "description": "Plaintext data detected"
        #                 }                        
        #                 continue
                    
        #             # value = row[0]
        #             # detected = self.get_weak_encryption_type(value)
        #             # print(f"[{table}.{column}] ▶ {value[:40]}... → {detected} 취약한 암호 알고리즘") # 결과
        #             # break
                    
        #     except Exception as e:
        #         print(f"⚠️ {table}.{column} 조회 실패: {e}")

        # conn.close()


if __name__ == "__main__":

    obj = CheckCryptographic()


    with open("../add_in/data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    source_files = data["source_files"]
    # obj.scan_file_for_hashes(source_files)

    with open("Cryptographic.json", "w", encoding="utf-8") as report_file:
        json.dump(obj.run(source_files), report_file, ensure_ascii=False, indent=2)

