"""
GUI 결과 포맷팅 유틸리티
검사 결과와 저장된 결과에서 동일한 포맷 사용
"""

def format_csrf_details(details):
    """A01 CSRF 상세 정보 포맷팅"""
    result = []
    
    # 보호 메커니즘
    protections = details.get("protections", [])
    if protections:
        result.append(f"• 보호 메커니즘: {', '.join(protections)}")
    else:
        result.append("• 보호 메커니즘: 없음")
    
    # SameSite Cookie
    samesite = details.get("samesite", False)
    result.append(f"• SameSite Cookie: {'설정됨' if samesite else '미설정'}")
    
    # CSRF 토큰
    tokens = details.get("tokens_found", [])
    if tokens:
        result.append(f"• CSRF 토큰: {len(tokens)}개 발견")
    else:
        result.append("• CSRF 토큰: 발견되지 않음")
    
    # 폼 분석
    forms = details.get("forms", [])
    if forms:
        post_forms = [f for f in forms if f.get("method") == "POST"]
        get_forms = [f for f in forms if f.get("method") == "GET"]
        
        result.append(f"• 전체 폼: {len(forms)}개")
        if post_forms:
            result.append(f"  - POST 폼: {len(post_forms)}개")
            forms_without_token = [f for f in post_forms if not f.get("tokens")]
            if forms_without_token:
                result.append(f"  - ⚠ CSRF 토큰 없는 POST 폼: {len(forms_without_token)}개")
        if get_forms:
            result.append(f"  - GET 폼: {len(get_forms)}개")
    
    # 설명
    description = details.get("description", "")
    if description:
        result.append(f"• 상세 설명: {description}")
    
    return "\n".join(result)


def format_common_details(detail_items, max_items=10):
    """일반적인 상세 정보 포맷팅 (A04, A05 등)"""
    result = []
    
    if not detail_items:
        return "상세 정보가 없습니다."
    
    # 여러 항목이 있는 경우 (배열)
    if isinstance(detail_items, list):
        result.append(f"• 총 {len(detail_items)}개 항목 발견\n")
        
        for idx, item in enumerate(detail_items[:max_items], 1):
            result.append(f"[{idx}]")
            
            # 위치 정보
            location = item.get('location') or item.get('url') or item.get('path', 'N/A')
            result.append(f"  • 위치: {location}")
            
            # 설명/이슈
            desc = item.get('description') or item.get('issue', 'N/A')
            result.append(f"  • 설명: {desc}")
            
            # HTTP 메서드
            method = item.get('method', '')
            if method:
                result.append(f"  • 메서드: {method}")
            
            result.append("")  # 빈 줄
        
        if len(detail_items) > max_items:
            result.append(f"... 외 {len(detail_items) - max_items}개 항목")
    
    # 단일 객체인 경우
    elif isinstance(detail_items, dict):
        for key, value in detail_items.items():
            if key not in ['test_id', 'test_name', 'risk_level']:
                result.append(f"• {key}: {value}")
    
    return "\n".join(result)


def format_library_details(detail_items, max_packages=10):
    """라이브러리 취약점 상세 정보 포맷팅 (A06) - 패키지별 그룹화"""
    result = []
    
    if not detail_items or not isinstance(detail_items, list):
        return "상세 정보가 없습니다."
    
    # 패키지별로 그룹화
    packages = {}
    for item in detail_items:
        pkg_name = item.get('package', 'Unknown')
        if pkg_name not in packages:
            packages[pkg_name] = []
        packages[pkg_name].append(item)
    
    # 요약 정보
    result.append(f"• 총 {len(detail_items)}개 취약점 발견")
    result.append(f"• 영향받는 패키지: {len(packages)}개\n")
    
    # 패키지별로 출력 (취약점 수가 많은 순서)
    sorted_packages = sorted(packages.items(), key=lambda x: len(x[1]), reverse=True)
    
    for pkg_idx, (pkg_name, vulns) in enumerate(sorted_packages[:max_packages], 1):
        result.append(f"📦 [{pkg_idx}] {pkg_name}")
        result.append("-" * 50)
        
        # 에코시스템
        ecosystem = vulns[0].get('ecosystem', 'N/A')
        result.append(f"  • 패키지 관리자: {ecosystem}")
        
        # 취약점 개수
        result.append(f"  • 발견된 취약점: {len(vulns)}개")
        
        # 취약점 ID 목록
        vuln_ids = [v.get('id', 'N/A') for v in vulns]
        if len(vuln_ids) <= 3:
            result.append(f"  • 취약점 ID: {', '.join(vuln_ids)}")
        else:
            result.append(f"  • 취약점 ID: {', '.join(vuln_ids[:3])}, ... 외 {len(vuln_ids) - 3}개")
        
        # 영향받는 버전
        all_versions = set()
        for v in vulns:
            versions = v.get('version', [])
            if versions:
                all_versions.update(versions)
        
        if all_versions:
            version_count = len(all_versions)
            if version_count <= 5:
                version_list = sorted(list(all_versions))
                result.append(f"  • 영향받는 버전: {', '.join(version_list)}")
            else:
                version_list = sorted(list(all_versions))[:5]
                result.append(f"  • 영향받는 버전: {version_count}개")
                result.append(f"    예시: {', '.join(version_list)}, ...")
        
        # 대표 취약점 설명 (첫 번째)
        first_vuln = vulns[0]
        description = first_vuln.get('description', '')
        if description:
            desc_text = description.replace('Details: ', '').strip()
            first_paragraph = desc_text.split('\n\n')[0]
            if len(first_paragraph) > 150:
                first_paragraph = first_paragraph[:150] + "..."
            result.append(f"  • 설명: {first_paragraph}")
        
        result.append("")  # 빈 줄
    
    if len(sorted_packages) > max_packages:
        result.append(f"... 외 {len(sorted_packages) - max_packages}개 패키지\n")
    
    # 에코시스템별 통계
    result.append("📊 에코시스템별 통계:")
    ecosystems = {}
    for pkg_name, vulns in packages.items():
        eco = vulns[0].get('ecosystem', 'Unknown')
        if eco not in ecosystems:
            ecosystems[eco] = 0
        ecosystems[eco] += len(vulns)
    
    for eco, count in sorted(ecosystems.items(), key=lambda x: x[1], reverse=True):
        result.append(f"  • {eco}: {count}개 취약점")
    
    return "\n".join(result)


def get_vulnerability_description(test_name):
    """취약점 유형별 설명 반환"""
    if "CSRF" in test_name:
        return ("• 취약점 설명: 공격자가 사용자의 권한을 도용하여 악의적인 요청을 실행할 수 있는 취약점입니다.\n"
               "• 권장 조치: CSRF 토큰 구현, SameSite 쿠키 속성 설정, Referer 검증")
    elif "Rate_Limit" in test_name:
        return ("• 취약점 설명: 요청 빈도 제한이 설정되지 않아 무차별 공격(브루트포스)이 가능한 취약점입니다.\n"
               "• 권장 조치: 요청 빈도 제한 설정, IP별 접근 제한 구현, 계정 잠금 정책 적용")
    elif "Permission" in test_name or "Access" in test_name:
        return ("• 취약점 설명: 인증 및 권한 검증이 부족하여 보호된 리소스에 접근할 수 있는 취약점입니다.\n"
               "• 권장 조치: 모든 보호 리소스에 인증 검증 추가, 권한별 접근 제어 강화")
    elif "XSS" in test_name:
        return ("• 취약점 설명: 웹 페이지에 악성 스크립트를 삽입하여 사용자의 브라우저에서 실행되는 취약점입니다.\n"
               "• 권장 조치: 입력값 검증 및 이스케이프 처리, Content Security Policy 적용, HttpOnly 쿠키 설정")
    elif "SQL" in test_name:
        return ("• 취약점 설명: 데이터베이스 쿼리에 악성 SQL 코드를 삽입하여 데이터베이스를 조작할 수 있는 취약점입니다.\n"
               "• 권장 조치: Prepared Statement 사용, 입력값 검증 강화, 데이터베이스 권한 최소화")
    elif "Command" in test_name or "Injection" in test_name:
        return ("• 취약점 설명: 시스템 명령어나 코드를 주입하여 서버를 조작할 수 있는 취약점입니다.\n"
               "• 권장 조치: 입력값 검증 및 살균 처리, 안전한 API 사용, 최소 권한 원칙 적용")
    elif "vulnerable" in test_name.lower() or "header" in test_name.lower():
        return ("• 취약점 설명: 보안 헤더가 누락되거나 민감한 정보가 HTTP 헤더를 통해 노출되는 취약점입니다.\n"
               "• 권장 조치: 보안 헤더 추가 (X-Frame-Options 등), 서버 정보 헤더 제거, HTTPS 강제 적용")
    elif "Library" in test_name or "Component" in test_name:
        return ("• 취약점 설명: 알려진 취약점이 있는 오래된 라이브러리를 사용하여 공격에 노출될 수 있는 취약점입니다.\n"
               "• 권장 조치: 라이브러리 최신 버전으로 업데이트, 정기적인 의존성 점검, 취약점 스캐닝 자동화")
    else:
        return (f"• 취약점 설명: {test_name} 관련 보안 취약점이 발견되었습니다.\n"
               "• 권장 조치: 상세한 보안 점검 수행, 보안 전문가 상담, 정기적인 취약점 점검")
