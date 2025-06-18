import yaml
import re
import argparse
import os
from github_repo_analyzer import GitHubRepoAnalyzer

class CICDPipelineAnalyzer(GitHubRepoAnalyzer):
    def analyze_file(self, file_path):
        issues = []
        content = self.get_file_content(file_path)
        if content is None:
            return issues

        if 'gitlab-ci.yml' in file_path or '.travis.yml' in file_path or 'azure-pipelines.yml' in file_path:
            issues.extend(self.analyze_yaml_pipeline(content, file_path))
        elif '.github/workflows' in file_path:
            issues.extend(self.analyze_github_actions(content, file_path))
        elif 'Jenkinsfile' in file_path:
            issues.extend(self.analyze_jenkinsfile(content, file_path))

        return issues

    def analyze_yaml_pipeline(self, content, file_path):
        issues = []
        try:
            pipeline = yaml.safe_load(content)
            # Check for exposed secrets
            if self.check_exposed_secrets(content):
                issues.append(f"Potential exposed secrets in {file_path}")
            
            # Check for insecure commands
            if self.check_insecure_commands(content):
                issues.append(f"Potential insecure commands in {file_path}")
            
            # Check for missing security scans
            if not self.check_security_scans(pipeline):
                issues.append(f"Missing security scans in {file_path}")
        except yaml.YAMLError:
            issues.append(f"Invalid YAML in {file_path}")
        return issues

    def analyze_github_actions(self, content, file_path):
        issues = []
        try:
            workflow = yaml.safe_load(content)
            # Check for exposed secrets
            if self.check_exposed_secrets(content):
                issues.append(f"Potential exposed secrets in {file_path}")
            
            # Check for insecure actions
            if self.check_insecure_actions(workflow):
                issues.append(f"Usage of potentially insecure actions in {file_path}")
        except yaml.YAMLError:
            issues.append(f"Invalid YAML in {file_path}")
        return issues

    def analyze_jenkinsfile(self, content, file_path):
        issues = []
        # Check for exposed secrets
        if self.check_exposed_secrets(content):
            issues.append(f"Potential exposed secrets in {file_path}")
        
        # Check for insecure practices
        if 'withCredentials' not in content:
            issues.append(f"Credentials might not be properly managed in {file_path}")
        return issues

    def check_exposed_secrets(self, content):
        secret_patterns = [
            r'password\s*=',
            r'api_key\s*=',
            r'secret\s*=',
            r'token\s*='
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in secret_patterns)

    def check_insecure_commands(self, content):
        insecure_patterns = [
            r'curl\s+.*\|\s*bash',
            r'wget\s+.*\|\s*bash',
            r'eval\s*\$\(',
        ]
        return any(re.search(pattern, content) for pattern in insecure_patterns)

    def check_security_scans(self, pipeline):
        # This is a basic check and should be expanded based on your specific requirements
        security_keywords = ['security', 'scan', 'lint', 'audit']
        return any(keyword in str(pipeline).lower() for keyword in security_keywords)

    def check_insecure_actions(self, workflow):
        for job in workflow.get('jobs', {}).values():
            for step in job.get('steps', []):
                if 'uses' in step and not step['uses'].startswith('actions/'):
                    return True
        return False

# New main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze CI/CD pipelines for security issues")
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

    analyzer = CICDPipelineAnalyzer(repo_name, args.access_token)
    issues = analyzer.scan_repository()

    # Write issues to files
    for i, issue in enumerate(issues, 1):
        with open(os.path.join(output_path, f"Alarm{i}.txt"), "w") as f:
            f.write(issue)

    print(f"Analysis complete. Results written to {output_path}")