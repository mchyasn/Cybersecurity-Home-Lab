import json
import requests
import argparse
import os
from github_repo_analyzer import GitHubRepoAnalyzer

class DependencyAnalyzer(GitHubRepoAnalyzer):
    def analyze_file(self, file_path):
        issues = []
        content = self.get_file_content(file_path)
        if content is None:
            return issues

        if file_path.endswith('package.json'):
            issues.extend(self.analyze_npm_dependencies(content))
        elif file_path.endswith('requirements.txt'):
            issues.extend(self.analyze_python_dependencies(content))

        return issues

    def analyze_npm_dependencies(self, content):
        issues = []
        try:
            package_json = json.loads(content)
            dependencies = package_json.get('dependencies', {})
            for package, version in dependencies.items():
                if version.startswith('^') or version.startswith('~'):
                    issues.append(f"Potentially insecure version range for {package}: {version}")
                
                # Check for known vulnerabilities (you'd need to implement or use a vulnerability database)
                # This is a placeholder for demonstration
                if self.check_npm_vulnerability(package, version):
                    issues.append(f"Potential vulnerability in {package} version {version}")
        except json.JSONDecodeError:
            issues.append("Invalid package.json file")
        return issues

    def analyze_python_dependencies(self, content):
        issues = []
        for line in content.splitlines():
            if '==' not in line:
                issues.append(f"Unpinned dependency: {line}")
            
            # Check for known vulnerabilities (you'd need to implement or use a vulnerability database)
            # This is a placeholder for demonstration
            package, version = line.split('==')
            if self.check_python_vulnerability(package, version):
                issues.append(f"Potential vulnerability in {package} version {version}")
        return issues

    def check_npm_vulnerability(self, package, version):
        # Placeholder: In a real scenario, you'd check against a vulnerability database
        return False

    def check_python_vulnerability(self, package, version):
        # Placeholder: In a real scenario, you'd check against a vulnerability database
        return False

# New main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze dependencies for security issues")
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

    analyzer = DependencyAnalyzer(repo_name, args.access_token)
    issues = analyzer.scan_repository()

    # Write issues to files
    for i, issue in enumerate(issues, 1):
        with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
            f.write(issue)

    print(f"Analysis complete. Results written to {output_path}")