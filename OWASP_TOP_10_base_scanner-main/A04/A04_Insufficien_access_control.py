import os
import stat
import json
from typing import List, Dict, Tuple, Optional

# from A04.A04_Rate_Limit import load_user_info


class PermissionAnalyzer:
    """파일 권한을 비트 연산으로 동적 분석하는 클래스"""
    
    # 권한 비트 상수
    READ = 4
    WRITE = 2
    EXECUTE = 1
    
    # 권한 레벨 정의
    OWNER_SHIFT = 6
    GROUP_SHIFT = 3
    OTHER_SHIFT = 0
    
    @staticmethod
    def extract_permissions(mode: int) -> Dict[str, int]:
        """권한 비트를 추출하여 소유자/그룹/기타별로 분리"""
        return {
            'owner': (mode >> PermissionAnalyzer.OWNER_SHIFT) & 7,
            'group': (mode >> PermissionAnalyzer.GROUP_SHIFT) & 7,
            'other': mode & 7
        }
    
    @staticmethod
    def has_permission(perm: int, check: int) -> bool:
        """특정 권한이 있는지 비트 AND 연산으로 확인"""
        return (perm & check) == check
    
    @staticmethod
    def is_world_writable(mode: int) -> bool:
        """전체 사용자 쓰기 권한 검사"""
        other_perm = mode & 7
        return PermissionAnalyzer.has_permission(other_perm, PermissionAnalyzer.WRITE)
    
    @staticmethod
    def is_world_readable(mode: int) -> bool:
        """전체 사용자 읽기 권한 검사"""
        other_perm = mode & 7
        return PermissionAnalyzer.has_permission(other_perm, PermissionAnalyzer.READ)
    
    @staticmethod
    def is_world_executable(mode: int) -> bool:
        """전체 사용자 실행 권한 검사"""
        other_perm = mode & 7
        return PermissionAnalyzer.has_permission(other_perm, PermissionAnalyzer.EXECUTE)
    
    @staticmethod
    def is_group_writable(mode: int) -> bool:
        """그룹 쓰기 권한 검사"""
        group_perm = (mode >> PermissionAnalyzer.GROUP_SHIFT) & 7
        return PermissionAnalyzer.has_permission(group_perm, PermissionAnalyzer.WRITE)
    
    @staticmethod
    def analyze_risk_level(mode: int, is_file: bool, is_directory: bool) -> Tuple[str, List[str]]:
        """권한의 위험도를 동적으로 분석"""
        risks = []
        risk_level = "LOW"
        
        perms = PermissionAnalyzer.extract_permissions(mode)
        
        # 위험한 권한 패턴 동적 검사
        if PermissionAnalyzer.is_world_writable(mode):
            risks.append("전체 사용자 쓰기 권한")
            risk_level = "HIGH"
        
        if PermissionAnalyzer.is_world_readable(mode) and is_file:
            risks.append("전체 사용자 읽기 권한 (파일)")
            if risk_level != "HIGH":
                risk_level = "MEDIUM"
        
        if PermissionAnalyzer.is_world_executable(mode):
            if is_directory:
                risks.append("전체 사용자 디렉토리 접근 권한")
            else:
                risks.append("전체 사용자 파일 실행 권한")
                risk_level = "HIGH"
        
        if PermissionAnalyzer.is_group_writable(mode):
            risks.append("그룹 쓰기 권한")
            if risk_level == "LOW":
                risk_level = "MEDIUM"

        
        # 특별한 권한 조합 검사
        if perms['owner'] == 7 and perms['group'] >= 5 and perms['other'] >= 5:
            risks.append("과도한 권한 조합 (755 이상)")
            risk_level = "HIGH"
        
        return risk_level, risks

ETC_PATH = "../etc/A04_critical_files.json"
USER_INFO_PATH = "../etc/user_info.json"

def read_file() -> Dict:
    with open(ETC_PATH, "r") as f:
        return json.load(f)

# def load_user_info() -> Dict:
    

class FileSystemAccessScanner:
    """불안전한 설계(A04): 파일 시스템 접근 제어 취약점 스캐너"""

    # 웹 개발 시 공통적으로 생성되는 민감한 디렉토리명
    COMMON_SENSITIVE_DIRS = {
        'config', 'conf', 'configuration',  # 설정 디렉토리
        'backup', 'backups', 'bak',         # 백업 디렉토리
        'upload', 'uploads', 'files', 'media', 'storage',  # 업로드 디렉토리
        'logs', 'log',                      # 로그 디렉토리
        'tmp', 'temp', 'cache',             # 임시 디렉토리
        'admin', 'administrator', 'private', 'secret',  # 관리자/비공개 디렉토리
        '.git', '.svn', '.hg',              # 버전 관리
        'db', 'database', 'data'            # 데이터베이스 디렉토리
    }

    # 웹 개발 시 공통적으로 생성되는 민감한 파일명 (확장자 포함)
    COMMON_SENSITIVE_FILES = {
        # 환경 설정 파일
        '.env', '.env.local', '.env.production', '.env.development',

        # PHP 설정 파일
        'config.php', 'configuration.php', 'settings.php',
        'wp-config.php', 'config.inc.php',

        # Python 설정 파일
        'settings.py', 'config.py', 'local_settings.py',

        # Node.js 설정
        'config.json', 'package.json',

        # Java 설정
        'application.properties', 'application.yml',

        # 데이터베이스 파일
        'database.yml', 'database.json', 'db.sqlite3',

        # 인증/보안 파일
        '.htpasswd', '.htaccess', 'auth.json', 'credentials.json',
        'secrets.json', 'jwt.secret',

        # 기타 설정
        'web.config', 'composer.json', 'Dockerfile'
    }

    # 백업/임시 파일 확장자
    BACKUP_EXTENSIONS = {
        '.bak', '.backup', '.old', '.tmp', '.swp', '.save', '.orig'
    }

    # 민감한 파일 확장자
    SENSITIVE_EXTENSIONS = {
        '.db', '.sqlite', '.sqlite3', '.sql', '.mdb',  # 데이터베이스
        '.log',                                         # 로그
        '.key', '.pem', '.crt', '.p12', '.pfx',        # 인증서/키
        '.env'                                          # 환경 변수
    }

    # 검사 제외 디렉토리 (용량이 크고 검사 불필요)
    EXCLUDE_DIRS = {
        'node_modules', 'vendor', 'bower_components',
        '.venv', 'venv', '__pycache__', '.pytest_cache',
        'dist', 'build', '.next', '.nuxt'
    }

    def __init__(self, max_depth: int = 3) -> None:
        """
        스캐너 초기화

        Args:
            max_depth: 검사할 최대 디렉토리 깊이 (기본값: 3)
        """
        self.max_depth = max_depth
        self.vulnerable_paths: List[Tuple[str, str, str]] = []
        self.items_tested_count = 0

        try:
            config_data = read_file()
            self.critical_files: List[str] = config_data.get("critical_files", [])
            self.sensitive_directories: List[str] = config_data.get("sensitive_directories", [])
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"설정 파일 로딩 실패 (기본값 사용): {e}")
            self.critical_files = []
            self.sensitive_directories = []
    
    def parse_scan_results(self: List[Dict]) -> List[Dict]:
        tests = []

        for (file_path, permission, reason) in self.vulnerable_paths:
            tests.append({
                "file": file_path,
                "permission": permission,
                "description": reason,
            })

        return tests 

    def should_check_file(self, filename: str) -> bool:
        """파일이 검사 대상인지 판단"""
        # 1. 민감한 파일명 (정확히 일치)
        if filename in self.COMMON_SENSITIVE_FILES:
            return True

        # 2. 백업 확장자
        if any(filename.endswith(ext) for ext in self.BACKUP_EXTENSIONS):
            return True

        # 3. 민감한 확장자
        if any(filename.endswith(ext) for ext in self.SENSITIVE_EXTENSIONS):
            return True

        # 4. 설정 파일 로드된 경우
        if filename in self.critical_files:
            return True

        return False

    def should_check_directory(self, dirname: str) -> bool:
        """디렉토리가 검사 대상인지 판단"""
        dirname_lower = dirname.lower()

        # 1. 제외 디렉토리
        if dirname in self.EXCLUDE_DIRS:
            return False

        # 2. 공통 민감한 디렉토리
        if dirname_lower in self.COMMON_SENSITIVE_DIRS:
            return True

        # 3. 패턴 매칭 (포함 여부)
        for pattern in self.COMMON_SENSITIVE_DIRS:
            if pattern in dirname_lower:
                return True

        # 4. 설정 파일 로드된 경우
        if dirname in self.sensitive_directories:
            return True

        return False

    def walk_and_check(self, directory_path: str, scan_log: List[str]) -> None:
        """
        지정된 경로를 재귀적으로 순회하며 권한을 검사 (선택적 검사)

        Args:
            directory_path: 검사할 디렉토리 경로
            scan_log: 검사 로그를 저장할 리스트
        """
        for current_dir, subdirs, filenames in os.walk(directory_path):
            # 현재 깊이 계산
            depth = current_dir.replace(directory_path, '').count(os.sep)
            if depth > self.max_depth:
                subdirs[:] = []  # 더 깊이 들어가지 않음
                continue

            # 제외 디렉토리 필터링
            subdirs[:] = [d for d in subdirs if d not in self.EXCLUDE_DIRS]

            # 현재 디렉토리명 추출
            current_dirname = os.path.basename(current_dir)

            # 민감한 디렉토리인 경우에만 권한 검사
            if self.should_check_directory(current_dirname):
                self._check_single_path_permission(current_dir, scan_log)

            # 파일 권한 검사 (선택적)
            for filename in filenames:
                # 검사 대상 파일인지 확인
                if self.should_check_file(filename):
                    file_path = os.path.join(current_dir, filename)
                    self._check_single_path_permission(file_path, scan_log)

    def _check_single_path_permission(self, target_path: str, scan_log: List[str]) -> None:
        """
        특정 파일/디렉토리의 권한을 검사하고 취약점 평가
        
        Args:
            target_path: 검사할 파일 또는 디렉토리 경로
            scan_log: 검사 로그를 저장할 리스트
        """
        if not os.path.exists(target_path):
            return

        # 검사 항목 카운트 증가
        self.items_tested_count += 1

        try:
            # 파일 권한 정보 획득
            stat_info = os.stat(target_path) # 파일 / 디렉토리의 상태 정보(모드, 소유자, 크기)
            permission_mode = stat.S_IMODE(stat_info.st_mode) # 파일 권한 비트 추출
            permission_octal = oct(permission_mode)[-3:]  # '755', '777' 등
            
            is_file = os.path.isfile(target_path)
            is_directory = os.path.isdir(target_path)
            filename = os.path.basename(target_path)
            
            # 로그 기록
            scan_log.append(f"[✓] 검사 대상: {target_path}")
            scan_log.append(f"    현재 권한: {permission_octal}")
            
            # 취약점 검사 (정수형 permission_mode 전달)
            vulnerability_info = self._analyze_permission_vulnerability(
                permission_mode, is_file, is_directory, filename
            )
            
            if vulnerability_info:
                scan_log.append(f"    취약점 발견: {vulnerability_info}")
                self.vulnerable_paths.append((target_path, permission_octal, vulnerability_info))
                
        except Exception as error:
            scan_log.append(f"    오류 발생: {str(error)}")
    
    def _analyze_permission_vulnerability(self, permission_mode: int, is_file: bool, is_directory: bool, filename: str) -> Optional[str]:
        """비트 연산을 사용한 개선된 권한 취약점 분석"""
        
        # 1. 동적 위험도 분석
        risk_level, risks = PermissionAnalyzer.analyze_risk_level(permission_mode, is_file, is_directory)
        
        if risks:
            primary_risk = risks[0]  # 가장 심각한 위험 사용
            
            # 2. 파일 타입별 특화 검사
            if is_file:
                # 중요 파일 특별 검사
                if filename in self.critical_files:
                    if PermissionAnalyzer.is_world_readable(permission_mode) or PermissionAnalyzer.is_group_writable(permission_mode):
                        return f"중요 파일 노출 위험: {primary_risk}"
                
                # 실행 파일 검사
                if PermissionAnalyzer.is_world_executable(permission_mode):
                    return f"실행 파일 보안 위험: {primary_risk}"
            
            elif is_directory:
                # 민감 디렉토리 검사
                if filename in self.sensitive_directories:
                    if PermissionAnalyzer.is_world_readable(permission_mode):
                        return f"민감 디렉토리 접근 위험: {primary_risk}"
                
                # 업로드 디렉토리 특별 검사
                if "upload" in filename.lower():
                    if PermissionAnalyzer.is_world_executable(permission_mode):
                        return f"업로드 디렉토리 실행 위험: {primary_risk}"
            
            # 3. 일반적인 위험한 권한
            if risk_level == "HIGH":
                return f"고위험 권한 설정: {primary_risk}"
            elif risk_level == "MEDIUM":
                return f"중위험 권한 설정: {primary_risk}"
        
        return None
    
    def run(self, source_file) ->  Dict:

        scan_log = []

        self.walk_and_check(source_file, scan_log)

        details= self.parse_scan_results()

        return details
    
def start_check_access_control(web_directory: str) -> List[Dict]:
    """
    접근 제어 검사를 실행하고 JSON 형식으로 결과 반환

    Args:
        web_root_directory: 검사 대상 웹 루트 디렉토리 경로

    Returns:
        검사 결과가 담긴 리스트
    """
    from datetime import datetime

    # web_directory가 비어있으면 빈 리스트 반환
    if not web_directory:
        print("⚠️ 검사 대상 디렉토리가 지정되지 않았습니다.")
        return []

    # 디렉토리가 존재하지 않으면 빈 리스트 반환
    if not os.path.exists(web_directory):
        print(f"⚠️ 디렉토리를 찾을 수 없습니다: {web_directory}")
        return []

    scanner = FileSystemAccessScanner()

    # 파일 시스템 스캔 실행
    scan_log: List[str] = []
    print(f"스캔 시작: {web_directory}")
    scanner.walk_and_check(web_directory, scan_log)

    # 스캔 로그 출력
    print("\n=== 스캔 로그 ===")
    for log_entry in scan_log:
        print(log_entry)
    print("======== 끝 =======\n")

    # 검사 결과를 JSON 형식으로 변환
    vulnerability_details = []
    for file_path, permission, reason in scanner.vulnerable_paths:
        vulnerability_details.append({
            "path": file_path,
            "method": "FILE_SYSTEM",
            "issue": f"{reason} (권한: {permission})",
            "timestamp": datetime.now().isoformat()
        })

    # ✅ 결과 반환 추가!
    return vulnerability_details


if __name__ == "__main__":
    import json
    try:
        with open(USER_INFO_PATH, "r") as f:
            config = json.load(f)
            web_directory = config["Web_Dir"]
    except Exception as e:
        print(f"설정 파일 로드 오류: {str(e)}")
 
    obj = FileSystemAccessScanner()
    # result = start_check_access_control(web_directory)
    result = obj.run(web_directory)

    with open("Insufficient_Access_Control_Result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # print(json.dumps(result, indent=2, ensure_ascii=False))