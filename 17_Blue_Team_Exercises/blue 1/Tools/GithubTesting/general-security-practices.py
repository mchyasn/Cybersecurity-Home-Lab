import argparse
import os
from github_repo_analyzer import GitHubRepoAnalyzer

class SecurityBestPracticesAnalyzer(GitHubRepoAnalyzer):
    def analyze_file(self, file_path):
        # This method is not used in this analyzer as we're focusing on repository-wide practices
        return []

    def scan_repository(self):
        issues = []

        # Check branch protection
        issues.extend(self.check_branch_protection())

        # Check for code signing
        issues.extend(self.check_code_signing())

        # Check for audit logging
        issues.extend(self.check_audit_logging())

        return issues

    def check_branch_protection(self):
        issues = []
        try:
            branch = self.repo.get_branch("main")
            if not branch.protected:
                issues.append("Main branch is not protected")
            else:
                protection = branch.get_protection()
                if not protection.required_pull_request_reviews:
                    issues.append("Pull request reviews are not required for merging to main")
                if not protection.required_status_checks:
                    issues.append("Status checks are not required for merging to main")
        except Exception as e:
            issues.append(f"Error checking branch protection: {str(e)}")
        return issues

    def check_code_signing(self):
        issues = []
        try:
            releases = self.repo.get_releases()
            for release in releases:
                if not release.body or "GPG key" not in release.body.lower():
                    issues.append(f"Release {release.title} may not be signed")
                break  # We only check the latest release for this example
        except Exception as e:
            issues.append(f"Error checking code signing: {str(e)}")
        return issues

    def check_audit_logging(self):
        issues = []
        try:
            # Check if there's a .github/workflows directory
            contents = self.repo.get_contents(".github/workflows")
            found_audit_workflow = False
            for content_file in contents:
                if 'audit' in content_file.name.lower():
                    found_audit_workflow = True
                    break
            if not found_audit_workflow:
                issues.append("No audit logging workflow found in .github/workflows")
        except Exception as e:
            issues.append(f"Error checking audit logging: {str(e)}")
        return issues

# New main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze general security practices")
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

    analyzer = SecurityBestPracticesAnalyzer(repo_name, args.access_token)
    issues = analyzer.scan_repository()

    # Write issues to files
    for i, issue in enumerate(issues, 1):
        with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
            f.write(issue)

    print(f"Analysis complete. Results written to {output_path}")