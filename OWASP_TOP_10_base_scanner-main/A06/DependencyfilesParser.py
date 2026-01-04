import json5, json
import logging

# logging.basicConfig(
#     filename="../logs/A06_DependencyfilesParser.log",
#     filemode='a',
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )   

class DependencyfilesParser:
    def __init__(self):
        pass

    def parse(self, file):
        try:
            logging.info("DependencyfilesParser - Parsing dependency file...")
            if not file or not isinstance(file, dict):
                logging.error(f"DependencyfilesParser - Error: Invalid file input")
                return []
                
            file_type = file.get("type")
            content_raw = file.get("content", "")
            
            if not file_type:
                logging.error(f"DependencyfilesParser - Error: No file type specified")
                return []
            
            if not content_raw:
                logging.warning(f"DependencyfilesParser - Warning: Empty content for {file_type}")
                return []
            
            # Handle different content types based on file type
            if file_type in ["requirements.txt", "setup.py", "yarn.lock", "go.mod", "go.sum", "pom.xml", "build.gradle", "Gemfile", "Gemfile.lock"]:
                # These files are plain text, don't parse as JSON
                logging.info(f"DependencyfilesParser - Treating {file_type} content as plain text")
                content = content_raw
            elif file_type in ["Pipfile", "pyproject.toml", "Cargo.toml", "Cargo.lock"]:
                # These files are TOML format, parse as TOML or handle as text
                try:
                    # Try to parse as TOML first, if toml library is available
                    try:
                        import toml
                        content = toml.loads(content_raw) if content_raw else {}
                    except ImportError:
                        logging.warning(f"DependencyfilesParser - TOML library not available for {file_type}, parsing as text")
                        # If toml library not available, pass as text for basic parsing
                        content = content_raw
                except Exception as e:
                    logging.error(f"DependencyfilesParser - Error parsing TOML for {file_type}: {e}")
                    # Fallback to text parsing
                    content = content_raw
            elif file_type in ["pnpm-lock.yaml"]:
                # YAML files
                try:
                    try:
                        import yaml
                        content = yaml.safe_load(content_raw) if content_raw else {}
                    except ImportError:
                        logging.warning(f"DependencyfilesParser - YAML library not available for {file_type}, skipping")
                        return []
                except Exception as e:
                    logging.error(f"DependencyfilesParser - Error parsing YAML for {file_type}: {e}")
                    return []
            else:
                # JSON-based files (package.json, composer.json, composer.lock, tsconfig.json)
                try:
                    content = json5.loads(content_raw) if content_raw else {}
                except Exception as e:
                    logging.error(f"DependencyfilesParser - Error parsing JSON for {file_type}: {e}")
                    return []
        
            if file_type == "requirements.txt":
                return self.parse_requirements_txt(content) # Parse requirements.txt
            elif file_type == "Pipfile":
                return self.parse_pipfile(content) # Parse Pipfile
            elif file_type == "pyproject.toml":
                return self.parse_pyproject_toml(content) # Parse pyproject.toml
            elif file_type == "setup.py":
                return self.parse_setup_py(content) # Parse setup.py
            elif file_type == "package.json":
                return self.parse_package_json(content) # Parse package.json
            elif file_type == "yarn.lock":
                return self.parse_yarn_lock(content) # Parse yarn.lock
            elif file_type == "pnpm-lock.yaml":
                return self.parse_pnpm_lock_yaml(content)  # Parse pnpm-lock.yaml
            elif file_type == "Cargo.toml":
                return self.parse_cargo_toml(content)  # Parse Cargo.toml
            elif file_type == "Cargo.lock":
                return self.parse_cargo_lock(content)  # Parse Cargo.lock
            elif file_type == "go.mod":
                return self.parse_go_mod(content) # Parse go.mod
            elif file_type == "go.sum":
                return self.parse_go_sum(content) # Parse go.sum
            elif file_type == "pom.xml":
                return self.parse_pom_xml(content) # Parse pom.xml
            elif file_type == "build.gradle":
                return self.parse_build_gradle(content) # Parse build.gradle
            elif file_type == "composer.json":
                return self.parse_composer_json(content) # Parse composer.json
            elif file_type == "composer.lock":
                return self.parse_composer_lock(content) # Parse composer.lock
            elif file_type == "Gemfile":
                return self.parse_gemfile(content) # Parse Gemfile
            elif file_type == "Gemfile.lock":
                return self.parse_gemfile_lock(content) # Parse Gemfile.lock
            else:
                print(f"Unsupported file type: {file_type}") 
                return []
                
        except Exception as e:
            print(f"Unexpected error in parse method: {e}")
            return []
    

    def parse_package_json(self, content: dict):
        logging.info("DependencyfilesParser - Parsing package.json content...")
        dependencies = []
        
        try:
            if not isinstance(content, dict):
                logging.error("DependencyfilesParser - Error: package.json content is not a dictionary")
                return []

            # Parse dependencies
            if "dependencies" in content and isinstance(content["dependencies"], dict):
                for package_name, version in content["dependencies"].items():
                    if isinstance(version, str):
                        clean_version = version.lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": clean_version, "ecosystem": "npm"})
                    else:
                        dependencies.append({"package_name": package_name, "version": None, "ecosystem": "npm"})

            # Parse devDependencies
            if "devDependencies" in content and isinstance(content["devDependencies"], dict):
                for package_name, version in content["devDependencies"].items():
                    if isinstance(version, str):
                        clean_version = version.lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": clean_version, "ecosystem": "npm"})
                    else:
                        dependencies.append({"package_name": package_name, "version": None, "ecosystem": "npm"})

            # Parse peerDependencies
            if "peerDependencies" in content and isinstance(content["peerDependencies"], dict):
                for package_name, version in content["peerDependencies"].items():
                    if isinstance(version, str):
                        clean_version = version.lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": clean_version, "ecosystem": "npm"})
                    else:
                        dependencies.append({"package_name": package_name, "version": None, "ecosystem": "npm"})

        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing package.json: {e}")

        return dependencies


    def parse_requirements_txt(self, content):
        logging.info("DependencyfilesParser - Parsing requirements.txt content...")
        dependencies = []
        
        try:
            if not isinstance(content, str):
                logging.error("DependencyfilesParser - Error: requirements.txt content is not a string")
                return []

            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        if "==" in line:
                            parts = line.split("==", 1)
                            if len(parts) == 2:
                                name, version = parts
                                dependencies.append({"package_name": name.strip(), "version": version.strip(), "ecosystem": "PyPI"})
                        elif ">=" in line:
                            parts = line.split(">=", 1)
                            if len(parts) == 2:
                                name, version = parts
                                dependencies.append({"package_name": name.strip(), "version": version.strip(), "ecosystem": "PyPI"})
                        elif "~=" in line:
                            parts = line.split("~=", 1)
                            if len(parts) == 2:
                                name, version = parts
                                dependencies.append({"package_name": name.strip(), "version": version.strip(), "ecosystem": "PyPI"})
                        else:
                            # Handle package names without version specifiers
                            clean_line = line.split()[0] if line.split() else line
                            dependencies.append({"package_name": clean_line, "version": None, "ecosystem": "PyPI"})
                    except Exception as e:
                        logging.error(f"Error parsing line '{line}': {e}")
                        continue
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing requirements.txt: {e}")
            
        return dependencies

    def parse_pipfile(self, content):
        logging.info("DependencyfilesParser - Parsing Pipfile content...")
        dependencies = []
        try:
            # Handle both dict (parsed TOML) and string (text) content
            if isinstance(content, str):
                # Parse as text using regex
                import re
                lines = content.splitlines()
                in_packages = False
                in_dev_packages = False
                
                for line in lines:
                    line = line.strip()
                    if line == '[packages]':
                        in_packages = True
                        in_dev_packages = False
                    elif line == '[dev-packages]':
                        in_packages = False
                        in_dev_packages = True
                    elif line.startswith('[') and line != '[packages]' and line != '[dev-packages]':
                        in_packages = False
                        in_dev_packages = False
                    elif (in_packages or in_dev_packages) and '=' in line:
                        # Parse package = "version" lines
                        match = re.match(r'^(\w+)\s*=\s*["\']([^"\']+)["\']', line)
                        if match:
                            package_name = match.group(1)
                            version = match.group(2).lstrip("^~<>=")
                            if version != "*":  # Skip wildcard versions
                                dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                            else:
                                dependencies.append({"package_name": package_name, "version": None, "ecosystem": "PyPI"})
                return dependencies
            
            elif not isinstance(content, dict):
                logging.error("DependencyfilesParser - Error: Pipfile content is not a dictionary or string")
                return []

            # Parse packages section
            if 'packages' in content and isinstance(content['packages'], dict):
                logging.info("DependencyfilesParser - Found packages in Pipfile")
                for package_name, version_info in content['packages'].items():
                    try:
                        if isinstance(version_info, str):
                            version = version_info.lstrip("^~<>=")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        elif isinstance(version_info, dict) and 'version' in version_info:
                            version = str(version_info['version']).lstrip("^~<>=")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        else:
                            dependencies.append({"package_name": package_name, "version": None, "ecosystem": "PyPI"})
                    except Exception as e:
                        logging.error(f"DependencyfilesParser - Error parsing package '{package_name}': {e}")
                        dependencies.append({"package_name": package_name, "version": None, "ecosystem": "PyPI"})

            # Parse dev-packages section
            if 'dev-packages' in content and isinstance(content['dev-packages'], dict):
                logging.info("DependencyfilesParser - Found dev-packages in Pipfile")
                for package_name, version_info in content['dev-packages'].items():
                    try:
                        if isinstance(version_info, str):
                            version = version_info.lstrip("^~<>=")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        elif isinstance(version_info, dict) and 'version' in version_info:
                            version = str(version_info['version']).lstrip("^~<>=")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        else:
                            dependencies.append({"package_name": package_name, "version": None, "ecosystem": "PyPI"})
                    except Exception as e:
                        logging.error(f"DependencyfilesParser - Error parsing dev package '{package_name}': {e}")
                        dependencies.append({"package_name": package_name, "version": None, "ecosystem": "PyPI"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing Pipfile: {e}")
        return dependencies

    def parse_pyproject_toml(self, content):
        logging.info("DependencyfilesParser - Parsing pyproject.toml content...")
        dependencies = []
        try:
            # Handle both dict (parsed TOML) and string (text) content
            if isinstance(content, str):
                # Parse as text using regex for basic dependency extraction
                import re
                
                # Look for dependencies in [project] section
                project_match = re.search(r'\[project\].*?dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if project_match:
                    deps_content = project_match.group(1)
                    # Extract individual dependencies
                    dep_pattern = r'["\']([^"\']+)["\']'
                    for dep_match in re.finditer(dep_pattern, deps_content):
                        dep = dep_match.group(1)
                        if '>=' in dep or '==' in dep or '>' in dep or '<' in dep or '^' in dep or '~' in dep:
                            name_match = re.match(r'^([^>=<^~]+)', dep)
                            if name_match:
                                package_name = name_match.group(1).strip()
                                version_match = re.search(r'([>=<^~]+)([^,\s]+)', dep)
                                version = version_match.group(2).lstrip("^~<>=") if version_match else None
                                dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        else:
                            dependencies.append({"package_name": dep.strip(), "version": None, "ecosystem": "PyPI"})
                
                return dependencies
            # Poetry dependencies
            if 'tool' in content and 'poetry' in content['tool']:
                poetry_data = content['tool']['poetry']
                if 'dependencies' in poetry_data:
                    for package_name, version_info in poetry_data['dependencies'].items():
                        if package_name != 'python':  # Skip python version
                            if isinstance(version_info, str):
                                version = version_info.lstrip("^~<>=")
                                dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                            elif isinstance(version_info, dict) and 'version' in version_info:
                                version = version_info['version'].lstrip("^~<>=")
                                dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                            else:
                                dependencies.append({"package_name": package_name, "version": None, "ecosystem": "PyPI"})
                                
                if 'dev-dependencies' in poetry_data:
                    for package_name, version_info in poetry_data['dev-dependencies'].items():
                        if isinstance(version_info, str):
                            version = version_info.lstrip("^~<>=")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        elif isinstance(version_info, dict) and 'version' in version_info:
                            version = version_info['version'].lstrip("^~<>=")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        else:
                            dependencies.append({"package_name": package_name, "version": None, "ecosystem": "PyPI"})

            # Standard pyproject.toml dependencies
            if 'project' in content:
                project_data = content['project']
                if 'dependencies' in project_data:
                    import re
                    for dep in project_data['dependencies']:
                        if '>=' in dep or '==' in dep or '>' in dep or '<' in dep or '^' in dep or '~' in dep:
                            match = re.match(r'^([^>=<^~]+)', dep)
                            if match:
                                package_name = match.group(1).strip()
                                version_match = re.search(r'([>=<^~]+)([^,\s]+)', dep)
                                version = version_match.group(2).lstrip("^~<>=") if version_match else None
                                dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                        else:
                            dependencies.append({"package_name": dep.strip(), "version": None, "ecosystem": "PyPI"})

        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing pyproject.toml: {e}")
        return dependencies

    def parse_setup_py(self, content):
        dependencies = []
        try:
            import re
            # Extract install_requires from setup.py
            install_requires_pattern = r'install_requires\s*=\s*\[(.*?)\]'
            match = re.search(install_requires_pattern, content, re.DOTALL)
            if match:
                requires_content = match.group(1)
                # Extract individual requirements
                req_pattern = r'[\'"]([^\'"]+)[\'"]'
                for req_match in re.finditer(req_pattern, requires_content):
                    req = req_match.group(1)
                    if '>=' in req or '==' in req or '>' in req or '<' in req or '^' in req or '~' in req:
                        name_match = re.match(r'^([^>=<^~]+)', req)
                        if name_match:
                            package_name = name_match.group(1).strip()
                            version_match = re.search(r'([>=<^~]+)([^,\s]+)', req)
                            version = version_match.group(2).lstrip("^~<>=") if version_match else None
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                    else:
                        dependencies.append({"package_name": req.strip(), "version": None, "ecosystem": "PyPI"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing setup.py: {e}")
        return dependencies


    def parse_yarn_lock(self, content):
        logging.info("DependencyfilesParser - Parsing yarn.lock content...")
        dependencies = []
        try:
            import re
            lines = content.splitlines()
            current_package = None
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Package declaration line
                    if '@' in line and not line.startswith(' '):
                        match = re.match(r'^"?([^@"]+)@([^"]+)"?:', line)
                        if match:
                            current_package = match.group(1)
                    elif line.startswith('version ') and current_package:
                        version = line.split('version ')[1].strip('"').lstrip("^~<>=")
                        dependencies.append({"package_name": current_package, "version": version, "ecosystem": "PyPI"})
                        current_package = None
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing yarn.lock: {e}")
        return dependencies

    def parse_pnpm_lock_yaml(self, content):
        logging.info("DependencyfilesParser - Parsing pnpm-lock.yaml content...")
        dependencies = []
        try:
            if 'dependencies' in content:
                for package_name, version_info in content['dependencies'].items():
                    if isinstance(version_info, str):
                        version = version_info.lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
                    elif isinstance(version_info, dict) and 'version' in version_info:
                        version = version_info['version'].lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "PyPI"})
        except Exception as e:
            print(f"Error parsing pnpm-lock.yaml: {e}")
        return dependencies

    def parse_cargo_toml(self, content):
        logging.info("DependencyfilesParser - Parsing Cargo.toml content...")
        dependencies = []
        try:
            # Handle both dict (parsed TOML) and string (text) content
            if isinstance(content, str):
                # Parse as text using regex
                import re
                lines = content.splitlines()
                in_dependencies = False
                
                for line in lines:
                    line = line.strip()
                    if line == '[dependencies]':
                        in_dependencies = True
                    elif line.startswith('[') and line != '[dependencies]':
                        in_dependencies = False
                    elif in_dependencies and '=' in line:
                        # Parse package = "version" lines
                        match = re.match(r'^(\w+)\s*=\s*["\']([^"\']+)["\']', line)
                        if match:
                            package_name = match.group(1)
                            version = match.group(2).lstrip("^~<>=")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "crates.io"})
                        else:
                            # Handle complex dependency definitions like { version = "1.0", features = [...] }
                            simple_match = re.match(r'^(\w+)\s*=\s*{.*?version\s*=\s*["\']([^"\']+)["\']', line)
                            if simple_match:
                                package_name = simple_match.group(1)
                                version = simple_match.group(2).lstrip("^~<>=")
                                dependencies.append({"package_name": package_name, "version": version, "ecosystem": "crates.io"})
                return dependencies
            
            elif 'dependencies' in content:
                for package_name, version_info in content['dependencies'].items():
                    if isinstance(version_info, str):
                        version = version_info.lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "crates.io"})
                    elif isinstance(version_info, dict) and 'version' in version_info:
                        version = version_info['version'].lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "crates.io"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing Cargo.toml: {e}")
        return dependencies

    def parse_cargo_lock(self, content):
        logging.info("DependencyfilesParser - Parsing Cargo.lock content...")
        dependencies = []
        try:
            # Handle both dict (parsed TOML) and string (text) content
            if isinstance(content, str):
                # Parse as text using regex
                import re
                
                # Find all [[package]] sections
                package_blocks = re.findall(r'\[\[package\]\].*?(?=\[\[package\]\]|\Z)', content, re.DOTALL)
                
                for block in package_blocks:
                    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', block)
                    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', block)
                    
                    if name_match and version_match:
                        package_name = name_match.group(1)
                        version = version_match.group(1)
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "crates.io"})
                
                return dependencies
            
            elif 'package' in content:
                for package in content['package']:
                    if 'name' in package and 'version' in package:
                        dependencies.append({"package_name": package['name'], "version": package['version'], "ecosystem": "crates.io"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing Cargo.lock: {e}")
        return dependencies

    def parse_go_mod(self, content):
        logging.info("DependencyfilesParser - Parsing go.mod content...")
        dependencies = []
        try:
            import re
            lines = content.splitlines()
            in_require = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('require'):
                    in_require = True
                    # Handle single line require
                    if not line.endswith('('):
                        parts = line.split()
                        if len(parts) >= 3:
                            package_name = parts[1]
                            version = parts[2].lstrip("v")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "Go"})
                elif in_require:
                    if line == ')':
                        in_require = False
                    elif line and not line.startswith('//'):
                        parts = line.split()
                        if len(parts) >= 2:
                            package_name = parts[0]
                            version = parts[1].lstrip("v")
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "Go"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing go.mod: {e}")
        return dependencies

    def parse_go_sum(self, content):
        logging.info("DependencyfilesParser - Parsing go.sum content...")
        dependencies = []
        try:
            lines = content.splitlines()
            seen = set()
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    package_name = parts[0]
                    version = parts[1].split('/')[0].lstrip("v")  # Remove hash part
                    if (package_name, version) not in seen:
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "Go"})
                        seen.add((package_name, version))
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing go.sum: {e}")
        return dependencies

    def parse_pom_xml(self, content):
        logging.info("DependencyfilesParser - Parsing pom.xml content...")
        dependencies = []
        try:
            import re
            # Simple regex-based parsing for Maven dependencies
            dep_pattern = r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?(?:<version>(.*?)</version>)?.*?</dependency>'
            matches = re.findall(dep_pattern, content, re.DOTALL)
            for match in matches:
                group_id, artifact_id, version = match
                package_name = f"{group_id.strip()}:{artifact_id.strip()}"
                ver = version.strip() if version else None
                dependencies.append({"package_name": package_name, "version": ver, "ecosystem": "Maven"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing pom.xml: {e}")
        return dependencies

    def parse_build_gradle(self, content):
        logging.info("DependencyfilesParser - Parsing build.gradle content...")
        dependencies = []
        try:
            import re
            lines = content.splitlines()
            in_dependencies = False
            
            for line in lines:
                line = line.strip()
                if 'dependencies' in line and '{' in line:
                    in_dependencies = True
                elif in_dependencies:
                    if '}' in line:
                        in_dependencies = False
                    else:
                        # Parse dependency declarations
                        dep_match = re.search(r'["\']([^:]+):([^:]+):([^"\']+)["\']', line)
                        if dep_match:
                            group = dep_match.group(1)
                            artifact = dep_match.group(2)
                            version = dep_match.group(3)
                            package_name = f"{group}:{artifact}"
                            dependencies.append({"package_name": package_name, "version": version, "ecosystem": "Maven"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing build.gradle: {e}")
        return dependencies

    def parse_composer_json(self, content):
        logging.info("DependencyfilesParser - Parsing composer.json content...")
        dependencies = []
        try:
            if 'require' in content:
                for package_name, version in content['require'].items():
                    if package_name != 'php':  # Skip PHP version
                        clean_version = version.lstrip("^~<>=")
                        dependencies.append({"package_name": package_name, "version": clean_version, "ecosystem": "Packagist"})
            
            if 'require-dev' in content:
                for package_name, version in content['require-dev'].items():
                    clean_version = version.lstrip("^~<>=")
                    dependencies.append({"package_name": package_name, "version": clean_version, "ecosystem": "Packagist"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing composer.json: {e}")
        return dependencies

    def parse_composer_lock(self, content):
        logging.info("DependencyfilesParser - Parsing composer.lock content...")
        dependencies = []
        try:
            if 'packages' in content:
                for package in content['packages']:
                    if 'name' in package and 'version' in package:
                        dependencies.append({"package_name": package['name'], "version": package['version'].lstrip("v"), "ecosystem": "Packagist"})
            
            if 'packages-dev' in content:
                for package in content['packages-dev']:
                    if 'name' in package and 'version' in package:
                        dependencies.append({"package_name": package['name'], "version": package['version'].lstrip("v"), "ecosystem": "Packagist"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing composer.lock: {e}")
        return dependencies

    def parse_gemfile(self, content):
        logging.info("DependencyfilesParser - Parsing Gemfile content...")
        dependencies = []
        try:
            import re
            lines = content.splitlines()
            
            for line in lines:
                line = line.strip()
                if line.startswith('gem '):
                    # Parse gem declarations
                    gem_match = re.match(r'gem\s+["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']+)["\'])?', line)
                    if gem_match:
                        package_name = gem_match.group(1)
                        version = gem_match.group(2).lstrip("^~<>=") if gem_match.group(2) else None
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "RubyGems"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing Gemfile: {e}")
        return dependencies

    def parse_gemfile_lock(self, content):
        logging.info("DependencyfilesParser - Parsing Gemfile.lock content...")
        dependencies = []
        try:
            import re
            lines = content.splitlines()
            in_gems = False
            
            for line in lines:
                line = line.strip()
                if line == 'GEM':
                    in_gems = True
                elif line.startswith('DEPENDENCIES') or line.startswith('PLATFORMS'):
                    in_gems = False
                elif in_gems and '(' in line and ')' in line:
                    # Parse gem with version
                    gem_match = re.match(r'(\S+)\s+\(([^)]+)\)', line)
                    if gem_match:
                        package_name = gem_match.group(1)
                        version = gem_match.group(2)
                        dependencies.append({"package_name": package_name, "version": version, "ecosystem": "RubyGems"})
        except Exception as e:
            logging.error(f"DependencyfilesParser - Error parsing Gemfile.lock: {e}")
        return dependencies

# sample =[
#   {
#     "type": "package.json",
#     "content": "{\n  \"name\": \"sample-project\",\n  \"version\": \"1.0.0\",\n  \"main\": \"index.js\",\n  \"scripts\": {\n    \"start\": \"node index.js\",\n    \"build\": \"tsc\"\n  },\n  \"dependencies\": {\n    \"express\": \"^4.18.2\"\n  },\n  \"devDependencies\": {\n    \"typescript\": \"^5.2.2\",\n    \"jest\": \"^29.6.2\"\n  }\n}"
#   },
#   {
#     "type": "tsconfig.json",
#     "content": "{\n  \"extends\": \"@tsconfig/node16/tsconfig.json\",\n  \"compilerOptions\": {\n    \"target\": \"ES2020\",\n    \"module\": \"CommonJS\",\n    \"outDir\": \"./dist\",\n    \"rootDir\": \"./src\",\n    \"strict\": true,\n    \"esModuleInterop\": true,\n    \"lib\": [\"ES2020\", \"DOM\"],\n    \"typeRoots\": [\"./node_modules/@types\"],\n    \"paths\": {\n      \"@/*\": [\"./src/*\"],\n      \"@types/*\": [\"./node_modules/@types/*\"]\n    }\n  },\n  \"include\": [\"src/**/*\"],\n  \"exclude\": [\"node_modules\"]\n}"
#   },
#   {
#     "type": "requirements.txt",
#     "content": "flask==2.3.2\nrequests==2.31.0\nnumpy==1.25.0\npandas==2.0.2"
#   },
#   {
#     "type": "Pipfile",
#     "content": "[[source]]\nname = \"pypi\"\nurl = \"https://pypi.org/simple\"\nverify_ssl = true\n\n[packages]\nflask = \"==2.3.2\"\nrequests = \"*\"\n\n[dev-packages]\npytest = \"*\"\n\n[requires]\npython_version = \"3.11\""
#   },
#   {
#     "type": "pyproject.toml",
#     "content": "[build-system]\nrequires = [\"setuptools>=61.0\"]\nbuild-backend = \"setuptools.build_meta\"\n\n[project]\nname = \"sample-python-project\"\nversion = \"0.1.0\"\ndependencies = [\n    \"requests>=2.31\",\n    \"flask>=2.3\"\n]"
#   },
#   {
#     "type": "setup.py",
#     "content": "from setuptools import setup, find_packages\n\nsetup(\n    name=\"sample-python-project\",\n    version=\"0.1.0\",\n    packages=find_packages(),\n    install_requires=[\n        \"flask>=2.3.2\",\n        \"requests>=2.31.0\"\n    ]\n)"
#   },
#   {
#     "type": "Cargo.toml",
#     "content": "[package]\nname = \"sample-rust-project\"\nversion = \"0.1.0\"\nedition = \"2021\"\n\n[dependencies]\ntokio = { version = \"1.28\", features = [\"full\"] }\nreqwest = \"0.11\""
#   },
#   {
#     "type": "Cargo.lock",
#     "content": "[[package]]\nname = \"tokio\"\nversion = \"1.28.0\"\n\n[[package]]\nname = \"reqwest\"\nversion = \"0.11.18\""
#   },
#   {
#     "type": "go.mod",
#     "content": "module github.com/example/sample-go-project\n\ngo 1.20\n\nrequire (\n    github.com/gin-gonic/gin v1.9.0\n    github.com/stretchr/testify v1.8.4\n)"
#   },
#   {
#     "type": "go.sum",
#     "content": "github.com/gin-gonic/gin v1.9.0 h1:...\ngithub.com/stretchr/testify v1.8.4 h1:..."
#   },
#   {
#     "type": "pom.xml",
#     "content": "<project xmlns=\"http://maven.apache.org/POM/4.0.0\">\n  <modelVersion>4.0.0</modelVersion>\n  <groupId>com.example</groupId>\n  <artifactId>sample-app</artifactId>\n  <version>1.0.0</version>\n  <dependencies>\n    <dependency>\n      <groupId>org.springframework.boot</groupId>\n      <artifactId>spring-boot-starter-web</artifactId>\n      <version>3.1.1</version>\n    </dependency>\n  </dependencies>\n</project>"
#   },
#   {
#     "type": "build.gradle",
#     "content": "plugins {\n    id 'java'\n    id 'org.springframework.boot' version '3.1.1'\n}\n\ndependencies {\n    implementation 'org.springframework.boot:spring-boot-starter-web:3.1.1'\n    testImplementation 'org.junit.jupiter:junit-jupiter:5.9.3'\n}"
#   },
#   {
#     "type": "composer.json",
#     "content": "{\n  \"name\": \"example/sample-php-project\",\n  \"require\": {\n    \"monolog/monolog\": \"^2.9\"\n  },\n  \"require-dev\": {\n    \"phpunit/phpunit\": \"^10.2\"\n  }\n}"
#   },
#   {
#     "type": "composer.lock",
#     "content": "{\n  \"packages\": [\n    {\n      \"name\": \"monolog/monolog\",\n      \"version\": \"2.9.1\"\n    }\n  ]\n}"
#   },
#   {
#     "type": "Gemfile",
#     "content": "source \"https://rubygems.org\"\n\ngem \"rails\", \"~> 7.0\"\ngem \"pg\", \">= 1.1\"\ngem \"puma\", \"~> 6.0\""
#   },
#   {
#     "type": "Gemfile.lock",
#     "content": "GEM\n  remote: https://rubygems.org/\n  specs:\n    rails (7.0.5)\n    pg (1.5.3)\n\nDEPENDENCIES\n  rails (~> 7.0)\n  pg (>= 1.1)"
#   }
# ]


# if __name__ == "__main__":
#     try:
#         with open("../add_in/data.json", "r", encoding="utf-8") as f:
#             files = json.loads(f.read())

#         obj = DependencyfilesParser()
        
#         # Use sample data for testing
#         dependencyfiles = sample
#         dependencyfiles = files["dependency_files"]
        
#         print("=== Dependency Files Parser Test ===\n")
        
#         for i, file in enumerate(dependencyfiles, 1):
#             try:
#                 file_type = file.get("type", "Unknown")
#                 print(f"{i}. Testing {file_type}...")
                
#                 result = obj.parse(file)
                
#                 if result:
#                     print(f"   ✅ Found {len(result)} dependencies:")
#                     for j, dep in enumerate(result, 1):  # Show all
#                         version_str = dep.get('version', 'No version') or 'No version'
#                         print(f"      {j}. {dep.get('package_name', 'Unknown')}: {version_str}")
#                     if len(result) > 3:
#                         print(f"      ... count {len(result)} ")
#                 else:
#                     print("   ❌ No dependencies found")
#                 print()
                
#             except Exception as e:
#                 print(f"   ❌ Error processing {file.get('type', 'Unknown')}: {e}\n")
#                 continue
        
#         print("=== Test Complete ===")
        
#     except Exception as e:
#         print(f"Fatal error: {e}")