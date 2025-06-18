import os
from github import Github
import base64
import argparse

class GitHubRepoAnalyzer:
    def __init__(self, repo_name, access_token):
        self.g = Github(access_token)
        self.repo = self.g.get_repo(repo_name)

    def get_file_content(self, file_path):
        try:
            file_content = self.repo.get_contents(file_path)
            content = base64.b64decode(file_content.content).decode('utf-8')
            return content
        except:
            return None

    def scan_repository(self):
        issues = []
        for content_file in self.repo.get_contents(""):
            if content_file.type == "dir":
                issues.extend(self.scan_directory(content_file.path))
            else:
                issues.extend(self.analyze_file(content_file.path))
        return issues

    def scan_directory(self, directory_path):
        issues = []
        for content_file in self.repo.get_contents(directory_path):
            if content_file.type == "dir":
                issues.extend(self.scan_directory(content_file.path))
            else:
                issues.extend(self.analyze_file(content_file.path))
        return issues

    def analyze_file(self, file_path):
        # This method will be overridden in each specific analyzer
        pass

    @staticmethod
    def run(analyzer_class):
        parser = argparse.ArgumentParser(description="Analyze GitHub repository")
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

        analyzer = analyzer_class(repo_name, args.access_token)
        issues = analyzer.scan_repository()

        # Write issues to files
        for i, issue in enumerate(issues, 1):
            with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
                f.write(issue)

        print(f"Analysis complete. Results written to {output_path}")

# Usage example (This part should be in each child script)
if __name__ == "__main__":
    class MySpecificAnalyzer(GitHubRepoAnalyzer):
        def analyze_file(self, file_path):
            # Implement specific analysis logic here
            pass

    GitHubRepoAnalyzer.run(MySpecificAnalyzer)
