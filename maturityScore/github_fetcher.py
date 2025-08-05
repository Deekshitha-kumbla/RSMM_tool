import requests
from urllib.parse import urlparse
import os
import aiohttp
from dotenv import load_dotenv
from .get_resoftmdata import GetRSMData
from .get_readme import GetReadme
from .get_softwarepmdata import GetSPMData
from .get_communitydata import GetCommunityData
from .get_adoptabilitydata import GetAdoptabilityData
import json 

GITHUB_API = "https://api.github.com"
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
readme=GetReadme()
spmdata=GetSPMData()
rsmdata=GetRSMData()
communitydata=GetCommunityData()
adoptabilitydata=GetAdoptabilityData()

def extract_repo_details(repo_url):
    parts = urlparse(repo_url).path.strip("/").split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    raise ValueError("Invalid GitHub URL format.")

def analyze_repo(repo_url):
    owner, repo = extract_repo_details(repo_url)

    headers = {
       "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"

    }

    repo_data = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=headers).json()
    commits = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/commits", headers=headers).json()
    contributors = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/contributors", headers=headers).json()

    breakdown = {
        #"README Present":  True if readme.get_readmefile(owner, repo, None) else False,
        #"Recent Commits": 10 if isinstance(commits, list) and len(commits) >= 5 else 0,
        #"Contributors": min(len(contributors), 10),
       # "License": 10 if repo_data.get("license") else 0,
       # "Stars": min(repo_data.get("stargazers_count", 0), 10),
        "Software Project Managmenet":{
        "Requirements":spmdata.requirementsCapability(repo_data, owner, repo),
        "Code quality and security":spmdata.get_codeQualitysecuritycapability(owner, repo),
        "Communication and collaboration": spmdata.get_communityCapability(owner, repo)
        },
        "Research Software Management":{
        "Impact measurement":rsmdata.detect_audience_and_impact_practices(owner, repo),
        "Sustainability": rsmdata.detect_sustainability_practices(owner, repo),
        "Visibility": rsmdata.detect_visibility_practices(owner, repo),
        "Ethics and Energy":rsmdata.detect_ethics_and_energy_practices(owner, repo),
        },
        "Community Engagement":{
        "Partnership":communitydata.detect_partnership_practices(owner, repo),
        "Community": communitydata.detect_community_practices(owner, repo),
        "Developers":communitydata.detect_developer_practices(owner, repo),
        "Licensing":communitydata.detect_license_practices(owner, repo),
        },
        "Software Adoptability":{
        "Ease of use":adoptabilitydata.detect_easeofuse_practices(owner, repo),
        "Documentation":adoptabilitydata.detect_documentation_practices(owner, repo),
        "Technology":adoptabilitydata.detect_developer_practices(owner, repo, repo_data),
        "Reproducibility":adoptabilitydata.detect_reproducibility_practices(owner, repo),
        "Education":adoptabilitydata.detect_educational_practices(owner, repo),
        "Deployment":adoptabilitydata.detect_deployment_practices(owner, repo),}
           }
    
    #total = sum(breakdown.values())
    #return {"total": total, "breakdown": breakdown}
    return {"breakdown": breakdown}
