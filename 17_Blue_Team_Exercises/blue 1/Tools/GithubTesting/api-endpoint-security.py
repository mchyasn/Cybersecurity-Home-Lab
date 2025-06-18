import yaml
import json
import re
import argparse
import os
from github_repo_analyzer import GitHubRepoAnalyzer

class APIEndpointAnalyzer(GitHubRepoAnalyzer):
    def analyze_file(self, file_path):
        issues = []
        content = self.get_file_content(file_path)
        if content is None:
            return issues

        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            issues.extend(self.analyze_openapi_spec(content))
        elif file_path.endswith('.py'):
            issues.extend(self.analyze_python_endpoints(content))
        elif file_path.endswith('.js'):
            issues.extend(self.analyze_javascript_endpoints(content))

        return issues

    def analyze_openapi_spec(self, content):
        issues = []
        try:
            spec = yaml.safe_load(content)
            paths = spec.get('paths', {})
            for path, methods in paths.items():
                for method, details in methods.items():
                    if 'security' not in details:
                        issues.append(f"Unsecured endpoint: {method.upper()} {path}")
                    if not details.get('parameters'):
                        issues.append(f"No input validation for: {method.upper()} {path}")
        except yaml.YAMLError:
            issues.append("Invalid OpenAPI specification file")
        return issues

    def analyze_python_endpoints(self, content):
        issues = []
        routes = re.findall(r'@.*\.route\([\'"](.+?)[\'"]\)', content)
        for route in routes:
            if not re.search(r'@login_required|auth\.login_required', content):
                issues.append(f"Potentially unsecured Python endpoint: {route}")
        return issues

    def analyze_javascript_endpoints(self, content):
        issues = []
        routes = re.findall(r'app\.(get|post|put|delete)\([\'"](.+?)[\'"]\)', content)
        for method, route in routes:
            if not re.search(r'isAuthenticated|requireAuth', content):
                issues.append(f"Potentially unsecured JavaScript endpoint: {method.upper()} {route}")
        return issues

# New main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze API endpoints for security issues")
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

    analyzer = APIEndpointAnalyzer(repo_name, args.access_token)
    issues = analyzer.scan_repository()

    # Write issues to files
    for i, issue in enumerate(issues, 1):
        with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
            f.write(issue)

    print(f"Analysis complete. Results written to {output_path}")
