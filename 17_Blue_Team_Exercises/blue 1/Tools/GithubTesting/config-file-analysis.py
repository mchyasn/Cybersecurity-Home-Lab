import re
import argparse
import os
from github_repo_analyzer import GitHubRepoAnalyzer

class ConfigFileAnalyzer(GitHubRepoAnalyzer):
    def analyze_file(self, file_path):
        issues = []
        content = self.get_file_content(file_path)
        if content is None:
            return issues

        # Check for exposed API keys
        if re.search(r"api_key\s*=\s*['\"][\w-]+['\"]", content):
            issues.append(f"Potential exposed API key in {file_path}")

        # Check for exposed tokens
        if re.search(r"token\s*=\s*['\"][\w-]+['\"]", content):
            issues.append(f"Potential exposed token in {file_path}")

        # Check for insecure settings in .env files
        if file_path.endswith('.env'):
            if "DEBUG=True" in content:
                issues.append(f"Debug mode enabled in {file_path}")

        # Check for insecure settings in CI/CD config files
        if 'circle' in file_path.lower() or 'travis' in file_path.lower():
            if re.search(r"password\s*:\s*\$\{\{", content):
                issues.append(f"Potential exposed secret in CI/CD config {file_path}")

        return issues

# New main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze configuration files for security issues")
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

    analyzer = ConfigFileAnalyzer(repo_name, args.access_token)
    issues = analyzer.scan_repository()

    # Write issues to files
    for i, issue in enumerate(issues, 1):
        with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
            f.write(issue)

    print(f"Analysis complete. Results written to {output_path}")
