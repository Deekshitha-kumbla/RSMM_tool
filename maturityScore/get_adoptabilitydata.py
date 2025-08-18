
import os
from dotenv import load_dotenv
from .get_softwarepmdata import GetSPMData
from .get_communitydata import GetCommunityData
import requests

spmdata = GetSPMData()
communitydata=GetCommunityData()



class GetAdoptabilityData:
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    
    headers = {
    "Accept": "application/vnd.github.v3+json", 
    "Authorization": f"token {token}"           
}
    COMMON_TECH = ["python", "r", "java", "c++", "javascript"]
    SCI_WORKFLOW_TOOLS = ["jupyter", "notebook", "snakemake", "nextflow", "scipy", "numpy", "matplotlib", "pandas"]
    RELEVANCE_KEYWORDS = ["technology review", "evaluate tools", "periodic review", "tool relevance"]
    REPLICATION_KEYWORDS = [
        "replication package", "reproduce results", "reproducible research",
        "reproduce the study", "replicate the experiment"
    ]
    WORKFLOW_KEYWORDS = [
        "research workflow", "integration", "pipeline", "automated analysis",
        "how to use in research"
    ]
    STANDARDIZED_WORKFLOW_TOOLS = [
        "snakemake", "nextflow", "cwl", "galaxy", "airflow", "nf-core"
    ]
    EDUCATION_KEYWORDS = [
        "tutorial", "training", "education", "teaching", "learn", "examples"
    ]
    IN_PERSON_KEYWORDS = [
        "workshop", "bootcamp", "training event", "in-person", "seminar"
    ]
    CURRICULUM_KEYWORDS = [
        "university", "course", "class", "syllabus", "curriculum", "MOOC"
    ]
    DEPLOYMENT_FILES = [
    "Dockerfile", "docker-compose.yml", "Makefile",
    ".github/workflows/deploy.yml", "heroku.yml",
    "k8s/", "helm/", "terraform/", "ansible/"
]

    DISTRIBUTED_KEYWORDS = [
    "mpi", "ray", "dask", "airflow", "slurm", "cluster", "distributed", "nodes", "parallel workflow"
]

    SBOM_FILES = [
    "sbom.json", "cyclonedx.json", "spdx.json"
]

    SBOM_KEYWORDS = [
    "sbom", "cyclonedx", "spdx", "syft", "bom"
]

    @staticmethod
    def detect_easeofuse_practices(owner, repo):
        readme = communitydata.get_file_content_lower(owner, repo, "README.md")
        docs_index = communitydata.get_file_content_lower(owner, repo, "docs/index.md")

        combined_text = readme + docs_index

        return {
            "Provide a statement of purpose": any(keyword in combined_text for keyword in [
                "project purpose", "goal", "objective", "mission", "what this project does", "why this project"
            ]),

            "Provide a simple how to use": any(keyword in combined_text for keyword in [
                "how to use", "getting started", "usage", "example usage", "run this", "quickstart", "installation"
            ]),

            "Provide online tutorials": any(keyword in combined_text for keyword in [
                "tutorial", "video guide", "walkthrough", "example notebook", "learn more", "documentation site"
            ])
        }
    @staticmethod
    def detect_documentation_practices(owner, repo):
        readme = communitydata.get_file_content_lower(owner, repo, "README.md")
        contributing = communitydata.get_file_content_lower(owner, repo, "CONTRIBUTING.md")
        docs_index = communitydata.get_file_content_lower(owner, repo, "docs/index.md")
        api_files = [
            "docs/api.md", "api.md", "openapi.yaml", "swagger.yaml",
            "docs/api-reference.md", "API_REFERENCE.md"
        ]

        return {
            "Provide a read me file with project explanation": "project" in readme and any(keyword in readme for keyword in [
                "overview", "description", "goal", "purpose"
            ]),

            "Provide a how-to guide": any(keyword in readme + contributing + docs_index for keyword in [
                "how to use", "getting started", "quickstart", "installation", "setup"
            ]),

            "Provide a common example usage": any(keyword in readme for keyword in [
                "example usage", "run this", "usage example", "command line example", "code example"
            ]),

            "Provide a documentation as repository/ documentation wiki": communitydata.file_exists(owner, repo, "docs/index.md") or communitydata.file_exists(owner, repo, "mkdocs.yml"),

            "Provide API documentation": any(communitydata.file_exists(owner, repo, fname) for fname in api_files)
        }
    @staticmethod
    def detect_developer_practices(owner, repo, repo_data):
        readme = communitydata.get_file_content_lower(owner, repo, "README.md")
        docs_index = communitydata.get_file_content_lower(owner, repo, "docs/index.md")
        combined = readme + docs_index

        # Check languages used
        languages_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
       
        langs = requests.get(languages_url, headers=GetAdoptabilityData.headers).json()
        detected_langs = [lang.lower() for lang in langs.keys()]
        common_tech_used = any(lang in GetAdoptabilityData.COMMON_TECH for lang in detected_langs)

        return {
            "Use common non-exotic or established technology": common_tech_used,
            "Facilitate integration into scientific workflow": any(tool in combined for tool in GetAdoptabilityData.SCI_WORKFLOW_TOOLS),
            "Evaluate technology relevance regularly": any(keyword in combined for keyword in GetAdoptabilityData.RELEVANCE_KEYWORDS)
        } 
        
        
    @staticmethod
    def detect_reproducibility_practices(owner, repo):
        combined_text = ""
        for file in ["README.md", "docs/README.md", "docs/index.md"]:
            combined_text += communitydata.get_file_content_lower(owner, repo, file)

        return {
            "Provide instructions on how to put into research workflow": any(k in combined_text for k in GetAdoptabilityData.WORKFLOW_KEYWORDS),
            "Provide instructions on how to make part of a replication package": any(k in combined_text for k in GetAdoptabilityData.REPLICATION_KEYWORDS),
            "Make part of standardized workflows": any(tool in combined_text for tool in GetAdoptabilityData.STANDARDIZED_WORKFLOW_TOOLS),
            "Make part of a replication package": any(fname in combined_text for fname in ["replication", "reproducibility", "replicate"])
        }
    @staticmethod
    def detect_educational_practices(owner, repo):
        files_to_check = [
            "README.md",
            "docs/README.md",
            "docs/tutorial.md",
            "docs/training.md",
            "education.md",
            "training.md"
        ]
        combined_text = ""
        for file in files_to_check:
            combined_text += communitydata.get_file_content_lower(owner, repo, file)

        return {
            "Develop generic educational materials": any(k in combined_text for k in GetAdoptabilityData.EDUCATION_KEYWORDS),
            "Organize training events in person": any(k in combined_text for k in GetAdoptabilityData.IN_PERSON_KEYWORDS),
            "Make project part of an educational program": any(k in combined_text for k in GetAdoptabilityData.CURRICULUM_KEYWORDS)
        }
    @staticmethod
    def detect_deployment_practices(owner, repo):
        # Check for deployment tool files
        deployment_tools = any(
            communitydata.file_exists(owner, repo, path)
            for path in [
                "Dockerfile", "docker-compose.yml", "Makefile",
                ".github/workflows/deploy.yml", "heroku.yml"
            ]
        )

        # Check for coordination/distributed workflow keywords
        content = ""
        for fname in ["README.md", "docs/deployment.md", "deployment.md"]:
            content += communitydata.get_file_content_lower(owner, repo, fname)

        coordination_mechanisms = any(word in content for word in [
            "mpi", "ray", "dask", "airflow", "slurm", "cluster", "distributed", "nodes"
        ])

        # SBOM file or mentions
        sbom_detected = any(
            communitydata.file_exists(owner, repo, sbom_file)
            for sbom_file in ["sbom.json", "cyclonedx.json", "spdx.json"]
        ) or any(word in content for word in ["sbom", "cyclonedx", "spdx", "syft", "software bill of materials"])

        # Multiple deployment configs 
        multiple_configs = sum([
            communitydata.file_exists(owner, repo, fname)
            for fname in ["Dockerfile", "heroku.yml", "k8s/deployment.yaml", "helm/values.yaml"]
        ]) >= 2

        return {
            "Provide with standard deployment tools": deployment_tools,
            "Enable deployment on a wide range of technology": multiple_configs,
            "Provide coordination mechanisms for  workflow distribution over different machines": coordination_mechanisms,
            "Generate SBOM": sbom_detected
        }