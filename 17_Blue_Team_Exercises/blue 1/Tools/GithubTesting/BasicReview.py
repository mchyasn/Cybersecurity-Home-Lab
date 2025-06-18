import os
import argparse
from github import Github
import base64

class GitHubRepoAnalyzer:
    def __init__(self, xml_file, business, asset_type, asset_value, access_token):
        self.xml_file = xml_file
        self.business = business
        self.asset_type = asset_type
        self.asset_value = asset_value
        self.access_token = access_token
        self.repo_name = self.format_repo_name(asset_value)
        self.g = Github(access_token)
        self.repo = self.g.get_repo(self.repo_name)
        self.base_output_dir = "C:/BugBounty/Results"
        self.analysis_type = "StaticCodeAnalysis"

    def format_repo_name(self, asset_value):
        formatted = asset_value.replace("https___", "https://").replace("_", "/")
        return formatted.replace("https://github.com/", "")

    def get_output_dir(self):
        return os.path.join(
            self.base_output_dir,
            self.business,
            self.asset_type,
            self.asset_value,
            self.analysis_type,
            self.__class__.__name__,
            "Techniques"
        )

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

    def save_results(self, issues):
        output_dir = self.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'alarm.txt')
        with open(output_file, 'w') as f:
            for issue in issues:
                f.write(f"{issue}\n")
        print(f"Results saved to {output_file}")

def main(analyzer_class):
    parser = argparse.ArgumentParser(description='GitHub Repository Analyzer')
    parser.add_argument('xml_file', help='Input XML file to scan')
    parser.add_argument('--business', required=True, help='Business name')
    parser.add_argument('--asset_type', required=True, help='Asset type')
    parser.add_argument('--asset_value', required=True, help='Asset value')
    parser.add_argument('--access_token', required=True, help='GitHub access token')

    args = parser.parse_args()

    analyzer = analyzer_class(args.xml_file, args.business, args.asset_type, args.asset_value, args.access_token)
    issues = analyzer.scan_repository()
    analyzer.save_results(issues)

# Usage in each specific analyzer script:
# if __name__ == "__main__":
#     main(SpecificAnalyzerClass)