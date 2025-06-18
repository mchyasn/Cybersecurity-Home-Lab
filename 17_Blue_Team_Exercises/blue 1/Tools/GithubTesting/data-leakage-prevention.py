import re
import argparse
import os
from github_repo_analyzer import GitHubRepoAnalyzer

class DataLeakageAnalyzer(GitHubRepoAnalyzer):
    def scan_repository(self):
        issues = []

        # Check for sensitive information in commits
        issues.extend(self.check_commits_for_sensitive_info())

        # Check repository visibility
        issues.extend(self.check_repository_visibility())

        # Check for sensitive files
        issues.extend(self.check_sensitive_files())

        return issues

    def check_commits_for_sensitive_info(self):
        issues = []
        commits = self.repo.get_commits()
        sensitive_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6011[0-9]{12}|622((12[6-9]|1[3-9][0-9])|([2-8][0-9][0-9])|(9(([0-1][0-9])|(2[0-5]))))[0-9]{10}|64[4-9][0-9]{13}|65[0-9]{14}|3(?:0[0-5]|[68][0-9])[0-9]{11}|3[47][0-9]{13})\b',  # Credit Card
            r'\b[A-Za-z0-9]{40}\b',  # Potential API Key
        ]
        for commit in commits[:100]:  # Limit to last 100 commits for performance
            for file in commit.files:
                if file.patch:
                    for pattern in sensitive_patterns:
                        if re.search(pattern, file.patch):
                            issues.append(f"Potential sensitive information in commit {commit.sha} in file {file.filename}")
        return issues

    def check_repository_visibility(self):
        issues = []
        if self.repo.private:
            return issues  # Private repositories are generally fine
        
        # Check for potentially sensitive files in public repos
        sensitive_files = ['.env', 'config.json', 'secrets.yaml']
        for file in sensitive_files:
            try:
                content = self.repo.get_contents(file)
                issues.append(f"Potentially sensitive file {file} found in public repository")
            except:
                pass  # File not found, which is good
        return issues

    def check_sensitive_files(self):
        issues = []
        sensitive_extensions = ['.pem', '.key', '.pkcs12', '.pfx', '.p12']
        contents = self.repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                if any(file_content.name.endswith(ext) for ext in sensitive_extensions):
                    issues.append(f"Potentially sensitive file found: {file_content.path}")
        return issues

# New main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze repository for potential data leakage")
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

    analyzer = DataLeakageAnalyzer(repo_name, args.access_token)
    issues = analyzer.scan_repository()

    # Write issues to files
    for i, issue in enumerate(issues, 1):
        with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
            f.write(issue)

    print(f"Analysis complete. Results written to {output_path}")