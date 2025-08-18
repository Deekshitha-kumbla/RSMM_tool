import os
from dotenv import load_dotenv
from .get_softwarepmdata import GetSPMData

spmdata = GetSPMData()


class GetCommunityData:
    

    @staticmethod
    def get_file_content_lower(owner, repo, fname):
        try:
            content = spmdata.get_file_content(owner, repo, fname)
            return content.lower() if content else ""
        except:
            return ""

    @staticmethod
    def find_keywords_in_files(owner, repo, files, keywords):
        for fname in files:
            content = GetCommunityData.get_file_content_lower(owner, repo, fname)
            if any(keyword in content for keyword in keywords):
                return True
        return False

    @staticmethod
    def file_exists(owner, repo, fname):
        try:
            return spmdata.get_file_content(owner, repo, fname) is not None
        except:
            return False
    @staticmethod
    def detect_partnership_practices(owner, repo):
      return {
        "Acknowledge partners and funding agencies on website": GetCommunityData.find_keywords_in_files(
           owner, repo, 
            ["README.md", "FUNDING.yml", "docs/funding.md", "docs/partners.md"],
            ["funding", "supported by", "sponsored", "grant", "funder", "acknowledgement", "donor", "backer", "nsf", "eu", "nih"]
        ),

        "Develop advanced partnership model": GetCommunityData.find_keywords_in_files(
           owner, repo, 
            ["README.md", "docs/partners.md", "docs/governance.md"],
            ["strategic partner", "consortium", "joint development", "collaboration model", "partnership framework", "mou", "industry partnership"]
        )
    }


    @staticmethod
    def detect_community_practices(owner, repo):
        return {
            "Impose community norms": GetCommunityData.file_exists(owner, repo, "CONTRIBUTING.md") or
                GetCommunityData.find_keywords_in_files(owner, repo, ["README.md", "docs/contributing.md", ".github/CONTRIBUTING.md"],
                                                        ["community norms", "guidelines", "contribution rules"]),
            "Onboard researchers as part of the community": GetCommunityData.find_keywords_in_files(owner, repo,
                ["CONTRIBUTING.md", "GETTING_STARTED.md", "README.md"],
                ["researcher onboarding", "first time contributor", "new contributor", "how to start"]),
            "Develop code of conduct": GetCommunityData.file_exists(owner, repo, "CODE_OF_CONDUCT.md") or
                GetCommunityData.file_exists(owner, repo, ".github/CODE_OF_CONDUCT.md"),
            "Appoint support team": GetCommunityData.find_keywords_in_files(owner, repo,
                ["README.md", "docs/support.md"],
                ["support team", "maintainers", "triage team"]),
            "Organize community events": GetCommunityData.find_keywords_in_files(owner, repo,
                ["README.md", "docs/events.md"],
                ["event", "hackathon", "webinar", "conference", "community meeting", "meetup"]),
            "Provide front page chat support": GetCommunityData.find_keywords_in_files(owner, repo,
                ["README.md"],
                ["gitter", "slack", "discord", "chat"]),
            "Focus on diversity and inclusion": GetCommunityData.find_keywords_in_files(owner, repo,
                ["CODE_OF_CONDUCT.md", "README.md", "DIVERSITY.md"],
                ["diversity", "inclusion", "inclusive", "equity", "underrepresented"])
        }

    @staticmethod
    def detect_developer_practices(owner, repo):
        return {
            "Make developer names and roles publicly available": any([
                GetCommunityData.file_exists(owner, repo, "MAINTAINERS.md"),
                GetCommunityData.file_exists(owner, repo, "CONTRIBUTORS.md"),
                GetCommunityData.find_keywords_in_files(owner, repo,
                    ["README.md", ".github/MAINTAINERS.md", ".github/CONTRIBUTORS.md"],
                    ["maintainers", "core team", "lead developer", "developer", "contributors"])
            ]),
            "Document how to join the team": GetCommunityData.file_exists(owner, repo, "CONTRIBUTING.md") or
                GetCommunityData.find_keywords_in_files(owner, repo,
                    ["README.md", "CONTRIBUTING.md", "docs/join.md"],
                    ["how to join", "become a maintainer", "join us", "contribute", "application process"]),
            "Set maximum response time for pull requests": GetCommunityData.find_keywords_in_files(owner, repo,
                ["CONTRIBUTING.md", "README.md"],
                ["respond within", "response time", "we review", "pull request turnaround"]),
            "Provide access to developer training and skill development": GetCommunityData.find_keywords_in_files(owner, repo,
                ["README.md", "docs/TRAINING.md", "TRAINING.md", "onboarding.md"],
                ["developer training", "mentorship", "onboarding", "learning", "skill development", "tutorials"])
        }
    @staticmethod
    def detect_license_practices(owner, repo):
        license_file = GetCommunityData.get_file_content_lower(owner, repo, "LICENSE")
        readme_file = GetCommunityData.get_file_content_lower(owner, repo, "README.md")

        return {
            "Select a license": GetCommunityData.file_exists(owner, repo, "LICENSE"),
            
            "Get institutional support for license choice": any(keyword in license_file + readme_file for keyword in [
                "institution", "university", "legal team", "tech transfer", "corporate counsel"
            ]),
            
            "Evaluate license policy regularly": any(keyword in readme_file for keyword in [
                "license review", "annually reviewed", "license update", "re-evaluated"
            ])
        }
        
    