from pathlib import Path
import json


LANG_EXT = {
    # 시스템/컴파일 언어
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".m": "Objective-C / MATLAB",
    ".mm": "Objective-C++",
    ".pas": "Pascal/Delphi",
    ".dpr": "Delphi",
    ".adb": "Ada",
    ".zig": "Zig",

    # 스크립트 언어
    ".js": "JavaScript",
    ".cjs": "JavaScript (CommonJS)",
    ".mjs": "JavaScript (ES Module)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript + JSX",
    ".jsx": "JavaScript + JSX",
    ".php": "PHP",
    ".phtml": "PHP (HTML Embedded)",
    ".php3": "PHP",
    ".php4": "PHP",
    ".php5": "PHP",
    ".phar": "PHP Archive",
    ".py": "Python",
    ".pyw": "Python (Windows GUI)",
    ".rb": "Ruby",
    ".pl": "Perl",
    ".pm": "Perl Module",
    # ".sh": "Shell Script",
    # ".bash": "Bash Script",
    # ".zsh": "Zsh Script",
    # ".ps1": "PowerShell",
    # ".psm1": "PowerShell Module",
    ".lua": "Lua",
    ".r": "R",

    # 프론트엔드 / 마크업
    ".html": "HTML",
    ".xhtml": "XHTML",
    ".css": "CSS",
    ".sass": "Sass",
    ".scss": "SCSS",
    ".less": "Less",
    ".vue": "Vue.js",
    ".svelte": "Svelte",
    ".hbs": "Handlebars",
    ".mustache": "Mustache",
    ".erb": "Ruby ERB Template",
    ".twig": "Twig Template",
    ".ejs": "EJS Template",
    ".pug": "Pug Template",
    ".j2": "Jinja2 Template",
    ".ex":"Elixir"
}

DEPENDENCY_FILES = [
    "package.json",
    "tsconfig.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "Pipfile",
    "pyproject.toml",
    "setup.py",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "pom.xml",
    "build.gradle",
    "composer.json",
    "composer.lock",
    "Gemfile",
    "Gemfile.lock"
] 

def data_processing(vulnerability_data, vuln_number, vulner_name):
    processed_data = {
        "categories": {
        "A01": {
            "category_name": "Broken Access Control",
            "tests": [
                {
                    "test_id": "A01-01", 
                    "test_name": "CSRF Protection",  
                    "risk_level": "", 
                    "pages_tested": 0,
                    "vulnerable_pages": 0,
                    "details": [] 
                }
            ]
        },
        
        }
    }

    {
        "caetegories": {
            vuln_number: {
                "category_name": vulner_name,
                "tests": [
                    {
                        "test_id": "",
                        "test_name": "",
                        "risk_level": "",
                        "pages_tested": 0,
                        "vulnerable_pages": 0,
                        "details": []
                    }
                ]
            }
        }
    }
    

    return json.dumps(processed_data, indent=2, ensure_ascii=False)
    # return processed_data



def format_project_data(sources, dependency_files):
    data_list = {
        "project_id" : "",
        "source_files" : [
            # {
            #     "path" : "",
            #     "language" : "",
            #     "context" : ""
            # }
        ],
        "dependency_files" :[
            # {
            #     "tpye" : "",
            #     "context" : ""
            # }
        ]
    }

    for path, (content, language) in sources.items():
        data_list["source_files"].append({
            "path": path,
            "language": language,
            "content": content
        })
        
    for name, content in dependency_files.items():
        data_list["dependency_files"].append({
            "type": name,
            "content": content
        })
        
    return data_list

def file_collection(path):
    base = Path(path)

    sources = {}
    dependency_files = {}
    
    for f in base.rglob("*/*"):  # 모든 하위 디렉토리 탐색
        
        if f.is_file():
            # context = f.read_text(encoding="utf-8", errors="ignore").replace("\n", "")

            if f.name in DEPENDENCY_FILES:
                try:
                    context = "".join(f.read_text(encoding="utf-8", errors="ignore"))
                    dependency_files[f.name] = context
                except Exception as e:
                    print(f"⚠️ {f} 읽기 실패: {e}")
                    
            elif f.suffix.lower() in list(LANG_EXT.keys()):
                try:
                    context = "".join(f.read_text(encoding="utf-8", errors="ignore"))
                    language = LANG_EXT[f.suffix.lower()]
                    sources[str(f.resolve())] = context, language
                except Exception as e:
                    print(f"⚠️ {f} 읽기 실패: {e}")


    return format_project_data(sources, dependency_files)

if __name__ == "__main__":
    import json
    # PrestaShop 프로젝트 경로 수정 (올바른 경로)
    file_li = file_collection("/home/ruqos/Desktop/project/WEB/PrestaShop")

    json_file_context = json.dumps(file_li, indent=2, ensure_ascii=False)


    with open("data.json", "w", encoding="utf-8") as f:
        f.write(json_file_context)
    print("data.json 파일이 생성되었습니다.")
    