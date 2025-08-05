import aiohttp
import asyncio
import re
import os
import requests
from dotenv import load_dotenv
import base64
from .get_softwarepmdata import GetSPMData
spmdata=GetSPMData()
class GetRSMData:
    
  token= os.getenv('GITHUB_TOKEN')
  headers = {"Accept": "application/vnd.github+json",
                
        "Authorization": f"token {token}"}
  GITHUB_API_BASE= "https://api.github.com"

  def __init__(self):
        self.data = None
    
  @staticmethod
  def find_keywords_in_files(owner, repo, files, keywords):
    for fname in files:
        content = spmdata.get_file_content(owner, repo, fname).lower()
        if any(keyword in content for keyword in keywords):
            return True
    return False
  @staticmethod
  def defines_clear_audience(owner, repo):
    candidate_files = ["README.md", "CONTRIBUTING.md", "docs/index.md"]
    audience_keywords = [
        "target audience", "intended users", "who is this for", "for developers",
        "for educators", "end users", "our users", "stakeholders"
    ]

    for fname in candidate_files:
        content = spmdata.get_file_content(owner, repo, fname).lower()
        if any(keyword in content for keyword in audience_keywords):
            return True
    return False
  @staticmethod
  def mentions_impact_measurement(owner, repo):
    files = ["README.md", "IMPACT.md", "docs/impact.md", "ANALYTICS.md"]
    keywords = ["impact", "measurement", "survey", "evaluation", "analytics", "metrics", "goal", "success"]

    for fname in files:
        content = spmdata.get_file_content(owner, repo, fname).lower()
        if any(word in content for word in keywords):
            return True
    return False
  @staticmethod
  def detect_audience_and_impact_practices(owner, repo):
    return {
        "Define a clear audience for the project": GetRSMData.defines_clear_audience(owner, repo),
        "Perform infrequent impact measurement": GetRSMData.mentions_impact_measurement(owner, repo),
        # "Evaluate whether the audience's goals are met":,
                     # "Perform continuous impact measurement": ,
                     # "Explore new audiences regularly":,
    }


  @staticmethod
  def detect_sustainability_practices(owner, repo):
    return {
        "Acquire temporary funding": GetRSMData.find_keywords_in_files(owner, repo, [
            "README.md", "FUNDING.md", "CITATION.cff", "docs/funding.md"
        ], ["grant", "funded by", "sponsored", "nsf", "nih", "eu horizon"]),

        "Write software management plan": GetRSMData.find_keywords_in_files(owner, repo, [
            "SOFTWARE_MANAGEMENT_PLAN.md", "MANAGEMENT.md", "README.md"
        ], ["software management plan", "project governance", "maintenance strategy"]),

        "Obtain support from a national research software center": GetRSMData.find_keywords_in_files(owner, repo, [
            "README.md", "docs/about.md", "CITATION.cff"
        ], ["software sustainability institute", "urssi", "numfocus", "chanzuckerberg", "mozilla science"]),

        "Acquire viable pathways for project sustainability": GetRSMData.find_keywords_in_files(owner, repo, [
            "README.md", "docs/roadmap.md", "docs/funding.md"
        ], ["sustainability", "long-term support", "business model", "sponsor", "donate", "backing"]),

        "Secure continuous funding": GetRSMData.find_keywords_in_files(owner, repo, [
            "README.md", "FUNDING.md"
        ], ["ongoing funding", "continuous support", "institutional funding", "renewed grant"]),

        "Define end-of-life policy": GetRSMData.find_keywords_in_files(owner, repo, [
            "README.md", "SECURITY.md", "docs/eol.md", "docs/maintenance.md"
        ], ["end-of-life", "eol", "sunset", "deprecation", "maintenance mode"])
    }
    
  @staticmethod
  def detect_visibility_practices(owner, repo):

    

       return {
        "Make code citable":  GetRSMData.find_keywords_in_files(
            owner, repo,["CITATION.cff", "README.md"],
            ["doi", "zenodo", "how to cite", "citation"]
        ),

        "Enable indexing of project meta-data":  GetRSMData.find_keywords_in_files(
          owner, repo,  ["CITATION.cff", "codemeta.json", "README.md"],
            ["metadata", "codemeta", "cff-version"]
        ),

        "Promote the project continuously": GetRSMData.find_keywords_in_files(
          owner, repo,  ["README.md"],
            ["twitter.com", "linkedin.com", "youtube.com", "blog", "newsletter", "follow us"]
        ),

        "Publish in a research software directory": GetRSMData.find_keywords_in_files(
           owner, repo, ["README.md", "docs/index.md"],
            ["ascl", "bio.tools", "scicrunch", "software directory"]
        ),

        "Acquire research software center acknowledgement":  GetRSMData.find_keywords_in_files(
            owner, repo,["README.md", "CITATION.cff"],
            ["software sustainability institute", "urssi", "numfocus", "mozilla science"]
        ),

        "Enable indexing of the project's source code":  GetRSMData.find_keywords_in_files(
           owner, repo, ["robots.txt", "sitemap.xml", ".github/settings.yml"],
            ["index", "search", "metadata"]
        ),

        "Garner industrial partner adoption":  GetRSMData.find_keywords_in_files(
           owner, repo, ["README.md", "docs/"],
            ["used by", "partner", "collaboration with", "industry", "adopted by"]
        )
    }
       
  @staticmethod
  def detect_ethics_and_energy_practices(owner, repo):
    
    return {
        "Analyze privacy usage impact": GetRSMData.find_keywords_in_files(
           owner, repo, 
            ["privacy.md", "README.md", "docs/privacy.md"],
            ["privacy", "gdpr", "personal data", "user data", "pii"]
        ),

        "Analyze ethical consequences of project use": GetRSMData.find_keywords_in_files(
           owner, repo, 
            ["README.md", "docs/ethics.md", "CODE_OF_CONDUCT.md"],
            ["ethics", "ethical", "bias", "harm", "misuse", "ai ethics"]
        ),

        "Document the cost of running the application": GetRSMData.find_keywords_in_files(
           owner, repo, 
            ["README.md", "docs/deployment.md", "cost.md"],
            ["cost", "cloud cost", "pricing", "resource usage", "billing"]
        ),

        "Consider total energy consumption": GetRSMData.find_keywords_in_files(
           owner, repo, 
            ["README.md", "sustainability.md", "docs/environment.md"],
            ["energy", "carbon", "green computing", "co2", "efficiency", "sustainability"]
        )
    }

  