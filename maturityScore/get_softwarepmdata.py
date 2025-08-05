import aiohttp
import asyncio
import re
import os
import requests
from dotenv import load_dotenv
import base64


class GetSPMData:
    
  token= os.getenv('GITHUB_TOKEN')
  headers = {"Accept": "application/vnd.github+json",
                
        "Authorization": f"token {token}"}
  GITHUB_API_BASE= "https://api.github.com"
  def __init__(self):
        self.data = None
    
  @staticmethod
  def get_additional_content(owner, repo, filename):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
   
    response = requests.get(url, headers=GetSPMData.headers)
    return response.status_code == 200
  @staticmethod
  def requirementsCapability(repo_data, owner, repo):
    capabilities = {
        "File issues in an issue tracker": False,
        "Act on feedback": False,
        "Manage requirements explicitly": False,
        "Perform release management": False,

        "Communicate roadmap": False
    }

    # Issue Tracker
    if repo_data.get("has_issues"):
        capabilities["File issues in an issue tracker"] = True

    # Feedback Handling (basic heuristic)
    comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments"
    comments_resp = requests.get(comments_url)
    if comments_resp.ok and len(comments_resp.json()) > 0:
        capabilities["Act on feedback"] = True

    # Explicit Requirements via Releases
    releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    releases_resp = requests.get(releases_url)
    if releases_resp.ok and len(releases_resp.json()) > 0:
        capabilities["Manage requirements explicitly"] = True
        capabilities["Perform release management"] = True


    

    # Roadmap Communication via ROADMAP.md or GitHub Projects
    if GetSPMData.get_additional_content(owner, repo, "ROADMAP.md"):
        capabilities["Communicate roadmap"] = True
    else:
        # Check GitHub Projects
        projects_url = f"https://api.github.com/repos/{owner}/{repo}/projects"
        headers = {"Accept": "application/vnd.github.inertia-preview+json",
                    "Authorization": f"token {GetSPMData.token}"}
        projects_resp = requests.get(projects_url, headers=headers)
        if projects_resp.ok and len(projects_resp.json()) > 0:
            capabilities["Communicate roadmap"] = True

    return capabilities
    
  @staticmethod
  def get_file_exists(owner, repo, path  ):
       url = f"{GetSPMData.GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
       response = requests.get(url, headers=GetSPMData.headers)
       return response.status_code == 200
  @staticmethod
  def get_file_content(owner, repo, path):
        url = f"{GetSPMData.GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(url, headers=GetSPMData.headers)
        if response.status_code == 200:
           content = response.json().get("content", "")
           return base64.b64decode(content).decode("utf-8")
        return ""
      

  def list_github_workflow_files(owner, repo):
        url = f"{GetSPMData.GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows"
        response = requests.get(url, headers=GetSPMData.headers)
        if response.status_code == 200:
           return [item["name"] for item in response.json() if item["name"].endswith(".yml")]
        return []

# -------------------- Feature Detection --------------------

  def has_coding_standard(owner, repo):
       files = [".pylintrc", ".flake8", ".editorconfig", ".eslintrc.json"]
       return any(GetSPMData.get_file_exists(owner, repo, f) for f in files)

  def conducts_code_reviews(owner, repo):
       url = f"{GetSPMData.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls?state=closed&per_page=10"
       response = requests.get(url, headers=GetSPMData.headers)
       if response.ok:
        for pr in response.json():
            if pr.get("merged_at") and (pr.get("requested_reviewers") or pr.get("review_comments", 0) > 0):
                return True
       return False

  def has_ci(owner, repo):
        return GetSPMData.get_file_exists(owner, repo, ".github/workflows")

  def has_executable_tests(owner, repo):
        return GetSPMData.get_file_exists(owner, repo, "tests") or GetSPMData.get_file_exists(owner, repo, "test")

  def uses_crash_reporting(owner, repo):
      for file in ["requirements.txt", "README.md"]:
        content = GetSPMData.get_file_content(owner, repo, file)
        if any(tool in content.lower() for tool in ["sentry", "rollbar", "bugsnag"]):
            return True
      return False

  def conducts_security_reviews(owner, repo):
      if GetSPMData.get_file_exists(owner, repo, "SECURITY.md"):
        return True
      for file in ["requirements.txt", ".github/workflows"]:
        content = GetSPMData.get_file_content(owner, repo, file)
        if any(tool in content.lower() for tool in ["bandit", "safety", "snyk"]):
            return True
      return False

  def defines_coverage_targets(owner, repo):
       files = [".coveragerc", ".codecov.yml", ".github/codecov.yml"]
       return any(GetSPMData.get_file_exists(owner, repo, f) for f in files)

  def runs_tests_in_workflow(owner, repo):
       files = GetSPMData.list_github_workflow_files(owner, repo)
       for wf in files:
        content = GetSPMData.get_file_content(owner, repo, f".github/workflows/{wf}")
        if any(cmd in content for cmd in ["pytest", "unittest", "nosetests"]):
            return True
       return False

  def follows_security_standards(owner, repo):
      return (
        GetSPMData.get_file_exists(owner, repo, "SECURITY.md") or
        GetSPMData.get_file_exists(owner, repo, ".github/dependabot.yml")
    )

# -------------------- Analyzer Function --------------------
  @staticmethod
  def get_codeQualitysecuritycapability(owner, repo):
      

      results = {
        "Provide a coding standard": GetSPMData.has_coding_standard(owner, repo),
        "Conduct code reviews": GetSPMData.conducts_code_reviews(owner, repo),
        "Implement continuous integration": GetSPMData.has_ci(owner, repo),
        "Provide executable tests": GetSPMData.has_executable_tests(owner, repo),
        "Use crash reporting": GetSPMData.uses_crash_reporting(owner, repo),
        "Conduct security reviews": GetSPMData.conducts_security_reviews(owner, repo),
        "Define code coverage targets": GetSPMData.defines_coverage_targets(owner, repo),
        "Execute tests in a public workflow": GetSPMData.runs_tests_in_workflow(owner, repo),
        "Follow an industry standard for security": GetSPMData.follows_security_standards(owner, repo)
       }

      return results
  def get_repo_metadata(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=GetSPMData.headers)
    return response.json() if response.ok else {}


# ----------- Feature Detectors -----------

  def is_public_repo(repo_data):
    return not repo_data.get("private", True)


  def uses_public_communication(owner, repo):
    keywords = ["discord", "slack", "gitter", "zulip", "matrix", "forum", "discussions"]
    for file in ["README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]:
        content = GetSPMData.get_file_content(owner, repo, file).lower()
        if any(word in content for word in keywords):
            return True
    return False


  def provides_newsletter(owner, repo):
    content = GetSPMData.get_file_content(owner, repo, "README.md").lower()
    return any(term in content for term in ["newsletter", "subscribe", "mailchimp", "substack"])


  def has_community_website(repo_data, owner, repo):
    if repo_data.get("homepage"):
        return True

    content = GetSPMData.get_file_content(owner, repo, "README.md").lower()
    if "community" in content and "http" in content:
        return True
    return False


# ----------- Main Analyzer -----------
  @staticmethod
  def get_communityCapability(owner, repo):
    repo_data = GetSPMData.get_repo_metadata(owner, repo)

    results = {
        "Store project in public repository with version control": GetSPMData.is_public_repo(repo_data),
        "Use public communication platform": GetSPMData.uses_public_communication(owner, repo),
        "Provide news letter": GetSPMData.provides_newsletter(owner, repo),
        "Provide community website": GetSPMData.has_community_website(repo_data, owner, repo)
    }

    return results