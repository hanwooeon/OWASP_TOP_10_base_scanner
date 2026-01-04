import re

class InjectionPatterns:
    def __init__(self):

        self.sql_patterns = [
            # Python SQL Injection patterns
            r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\s+.*\s*(WHERE|FROM|INTO|VALUES)\s*.*[\'\"]\s*\+\s*[\w\.\[\]]+',
            r'f[\'\"](SELECT|INSERT|UPDATE|DELETE).*\{.*\}.*[\'\"]\)',
            r'(cursor\.execute|execute)\s*\(\s*[\'\"](SELECT|INSERT|UPDATE|DELETE).*[\'\"]\s*\+',
            r'(cursor\.execute|execute)\s*\(\s*f[\'\"](SELECT|INSERT|UPDATE|DELETE).*\{.*\}',
            r'(query|sql)\s*=\s*[\'\"](SELECT|INSERT|UPDATE|DELETE).*[\'\"]\s*\+',
            r'(query|sql)\s*=\s*f[\'\"](SELECT|INSERT|UPDATE|DELETE).*\{.*\}',
            
            # JavaScript/TypeScript SQL Injection patterns  
            r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\s+.*\s*(WHERE|FROM|INTO|VALUES).*`[^`]*\$\{[^}]*\}',
            r'`(SELECT|INSERT|UPDATE|DELETE).*\$\{[^}]*\}.*`',
            r'(query|sql)\s*=\s*`(SELECT|INSERT|UPDATE|DELETE).*\$\{[^}]*\}',
            r'(connection\.query|db\.query|pool\.query)\s*\(\s*.*[+`]',
            r'(sequelize\.query|knex\.raw)\s*\(\s*.*[+`]',
            
            # Node.js ORM patterns (unsafe)
            r'\.where\s*\(\s*.*[+`]',
            r'\.having\s*\(\s*.*[+`]',
            r'\.orderBy\s*\(\s*.*[+`]'
        ]
        
        self.xss_patterns = [
            # DOM Manipulation (basic)
            r'innerHTML\s*=\s*.*[+`]',
            r'outerHTML\s*=\s*.*[+`]',
            r'insertAdjacentHTML\s*\([^,]+,\s*.*[+`]',
            r'insertAdjacentText\s*\([^,]+,\s*.*[+`]',
            
            # Document Methods
            r'document\.write\s*\(\s*.*[+`]',
            r'document\.writeln\s*\(\s*.*[+`]',
            
            # jQuery Methods
            r'\$\([^)]+\)\.html\s*\(\s*.*[+`]',
            r'\$\([^)]+\)\.append\s*\(\s*.*[+`]',
            r'\$\([^)]+\)\.prepend\s*\(\s*.*[+`]',
            r'\$\([^)]+\)\.after\s*\(\s*.*[+`]',
            r'\$\([^)]+\)\.before\s*\(\s*.*[+`]',
            
            # Template Literals (unsafe)
            r'innerHTML\s*=\s*`[^`]*\$\{[^}]*\}',
            r'outerHTML\s*=\s*`[^`]*\$\{[^}]*\}',
            
            # React dangerouslySetInnerHTML
            r'dangerouslySetInnerHTML\s*:\s*\{\s*__html\s*:\s*.*[+`]',
            
            # Angular bypassSecurityTrustHtml
            r'bypassSecurityTrustHtml\s*\(\s*.*[+`]',
            
            # Event Handler Injection
            r'setAttribute\s*\(\s*[\'\"](on\w+)[\'\"]\s*,\s*.*[+`]',
            r'\w+\.on\w+\s*=\s*.*[+`]',
            
            # Original patterns
            r'\.append\s*\(\s*.*\+.*\)',
            r'\.html\s*\(\s*.*\+.*\)'
        ]
        
        self.command_patterns = [
            # Python Command Injection
            r'(os\.system|subprocess\.|exec|eval)\s*\(\s*.*[+`]',
            r'(os\.popen|os\.spawn)\s*\(\s*.*[+`]',
            
            # JavaScript Command Injection
            r'eval\s*\(\s*.*[+`]',
            r'Function\s*\(\s*.*[+`]',
            r'setTimeout\s*\(\s*.*[+`]',
            r'setInterval\s*\(\s*.*[+`]',
            
            # Node.js Child Process
            r'child_process\.exec\s*\(\s*.*[+`]',
            r'child_process\.execSync\s*\(\s*.*[+`]',
            r'child_process\.spawn\s*\(\s*.*[+`]',
            r'require\s*\(\s*[\'\"](child_process)[\'\"].*\.exec\s*\(\s*.*[+`]',
            
            # Browser APIs (unsafe)
            r'fetch\s*\(\s*.*[+`]',
            r'XMLHttpRequest.*\.open\s*\([^,]+,\s*.*[+`]',
            
            # PHP Command Injection
            r'(system|shell_exec|exec|passthru)\s*\(\s*.*[+`.]',
            
            # Java Command Injection
            r'(Runtime\.getRuntime\(\)\.exec)\s*\(\s*.*[+`]',
            r'(ProcessBuilder)\s*\(\s*.*[+`]'
        ]
    
    def parse_scan_results(self, vulnerabilities):
        
        details = []

        if not vulnerabilities:
            return {}

        for vuln in vulnerabilities:
            details.append({
                    "file": vuln['path'],
                    "line": vuln['line'],
                    "pattern": vuln['pattern']
                }
            )

        return details

    def sqli_run(self, source_files):

        result = self.swordsman(source_files, self.sql_patterns)

        return self.parse_scan_results(result)

    def xss_run(self, source_files):

        result = self.swordsman(source_files, self.xss_patterns)

        return self.parse_scan_results(result)


    def command_injection_run(self, source_files):

        result = self.swordsman(source_files, self.command_patterns)

        return self.parse_scan_results(result)

    def swordsman(self, source_files, patterns = None): #패턴 검사
        vulnerabilities = list()

        for source in source_files:
            code = source["content"].splitlines()
            for line_num, line in enumerate(code, 1):
                if line.strip().startswith(("//", "#", "/*", "*", "*/")):
                    continue
                path = source["path"]
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append(
                            {
                                "path": path,
                                "line": str(line_num),
                                "pattern" : pattern
                            }
                        )
                        # self.num+=1
                        break  # 한 줄에 여러 패턴이 걸려도 한 번만 기록
        
        return vulnerabilities
    

if __name__ == "__main__":
    import json
    
    with open("../add_in/data.json", "r", encoding="utf-8") as f:
        source_files = json.load(f)

    source_files = source_files["source_files"]
    
    obj = InjectionPatterns()

    result1 = obj.sqli_run(source_files)
    result2 = obj.xss_run(source_files)
    result3 = obj.command_injection_run(source_files)

    with open("./sqli.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(result1, indent=2, ensure_ascii=False))

    with open("./xss.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(result2, indent=2, ensure_ascii=False))

    with open("./command_injection.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(result3, indent=2, ensure_ascii=False))
    
    
