import re
import argparse
import os
from github_repo_analyzer import GitHubRepoAnalyzer

class DocsScriptsAnalyzer(GitHubRepoAnalyzer):
    def analyze_file(self, file_path):
        issues = []
        content = self.get_file_content(file_path)
        if content is None:
            return issues

        if file_path.endswith('.md') or file_path.endswith('.txt'):
            issues.extend(self.analyze_documentation(content, file_path))
        elif file_path.endswith('.sh') or file_path.endswith('.bash'):
            issues.extend(self.analyze_shell_script(content, file_path))
        elif file_path.endswith('.py'):
            issues.extend(self.analyze_python_script(content, file_path))

        return issues

    def analyze_documentation(self, content, file_path):
        issues = []
        # Check for exposed credentials
        if re.search(r'password\s*=\s*[\'"][^\'"]+[\'"]', content):
            issues.append(f"Potential exposed password in {file_path}")
        
        # Check for internal URLs
        if re.search(r'https?://internal\.', content):
            issues.append(f"Potential internal URL exposed in {file_path}")
        
        return issues

    def analyze_shell_script(self, content, file_path):
        issues = []
        # Check for insecure practices
        if 'curl' in content and '| bash' in content:
            issues.append(f"Potentially insecure 'curl | bash' pattern in {file_path}")
        
        # Check for hardcoded secrets
        if re.search(r'export\s+\w+_SECRET=', content):
            issues.append(f"Potential hardcoded secret in {file_path}")
        
        return issues

    def analyze_python_script(self, content, file_path):
        issues = []
        # Check for use of 'exec' or 'eval'
        if 'exec(' in content or 'eval(' in content:
            issues.append(f"Use of 'exec' or 'eval' in {file_path}")
        
        # Check for hardcoded credentials
        if re.search(r'password\s*=\s*[\'"][^\'"]+[\'"]', content):
            issues.append(f"Potential hardcoded password in {file_path}")
        
        return issues

# New main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze documentation and scripts for security issues")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")
    parser.add_argument("--access_token", required=True, help="GitHub access token")
    parser.add_argument("--base_url", required=True, help="Base URL for output path")
    args = parser.parse_args()

    # Process asset_value to get repo_name
    repo_name = args.asset_value.replace("https___", "https://").replace("_", "/")
    repo_name = repo_name.replace("https://github.com/", "")

    # Build output path
    output_path = os.path.join(
        args.base_url,
        args.business,
        args.asset_type,
        args.asset_value,
        "StaticCodeAnalysis"
    )
    os.makedirs(output_path, exist_ok=True)

    analyzer = DocsScriptsAnalyzer(repo_name, args.access_token)
    issues = analyzer.scan_repository()

    # Write issues to files
    for i, issue in enumerate(issues, 1):
        with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
            f.write(issue)

    print(f"Analysis complete. Results written to {output_path}")
