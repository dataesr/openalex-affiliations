#!/usr/bin/env python3
# Execution example: python3 sync_openalex_affiliations_github_issues.py

# Imports
from dotenv import load_dotenv
import os
import pandas as pd
import requests
import time

load_dotenv()

# Config
GITHUB_PER_PAGE = 100
GITHUB_REPOSITORY_NAME = "dataesr/openalex-affiliations"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
ODS_API_KEY = os.getenv("ODS_API_KEY")
ODS_DATASET = "https://data.enseignementsup-recherche.gouv.fr/api/automation/v1.0/datasets/da_lyihp9"
OUTPUT_FILE_NAME = "github_issues.csv"

# Functions
def collect_issues():
    all_issues = []
    for p in range(1, 10000):
        print(p)
        # Wait for 1 second between 2 API calls
        time.sleep(1)
        issues_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY_NAME}/issues?per_page={GITHUB_PER_PAGE}&page={p}&state=all"
        gh_session = requests.Session()
        gh_session.auth = (GITHUB_USERNAME, GITHUB_TOKEN)
        issues = gh_session.get(issues_url).json()
        if len(issues) < GITHUB_PER_PAGE:
            break
        all_issues += issues
    return all_issues

def parse_issue(issue):
    new_elt = {}
    new_elt["github_issue_id"] = issue["number"]
    new_elt["github_issue_link"] = f"https://github.com/dataesr/openalex-affiliations/issues/{issue['number']}"
    new_elt["state"] = issue["state"]
    new_elt["date_opened"] = issue["created_at"][0:10]
    new_elt["date_closed"] = None if issue["closed_at"] is None else issue["closed_at"][0:10]
    a = "\nraw_affiliation_name: "
    b = "\nnew_rors: "
    c = "\nprevious_rors: "
    d = "\nworks_examples: "
    e = "\ncontact: "
    a_start = issue["body"].find(a) + len(a)
    a_end = issue["body"].find(b)
    b_start = a_end + len(b)
    b_end = issue["body"].find(c)
    c_start = b_end + len(c)
    c_end = issue["body"].find(d)
    d_start = c_end + len(d)
    d_end = issue["body"].find(e)
    e_start = d_end + len(e)
    e_end = len(issue["body"])-1
    new_elt["raw_affiliation_name"] = issue["body"][a_start:a_end]
    new_rors = [r for r in issue["body"][b_start:b_end].split(";") if r]
    previous_rors = [r for r in issue["body"][c_start:c_end].split(";") if r]
    added_rors = list(set(new_rors) - set(previous_rors))
    removed_rors = list(set(previous_rors) - set(new_rors))
    new_elt["has_added_rors"] = 1 if len(added_rors) > 0 else 0
    new_elt["has_removed_rors"] = 1 if len(removed_rors) > 0 else 0
    new_elt["new_rors"] = ";".join(new_rors)
    new_elt["previous_rors"] = ";".join(previous_rors)
    new_elt["added_rors"] = ";".join(added_rors)
    new_elt["removed_rors"] = ";".join(removed_rors)
    new_elt["openalex_works_examples"] = ";".join([f"https://api.openalex.org/works/{work}" for work in issue["body"][d_start:d_end].split(";")])
    if e_start > d_start:
        new_elt["contact"] = issue["body"][e_start:e_end]
        if "@" in new_elt["contact"]:
            new_elt["contact_domain"] = new_elt["contact"].split("@")[1].strip()
    return new_elt

def ods_sync():
    url = f"{ODS_DATASET}/resources/files/"
    headers = { "Authorization": f"apikey {ODS_API_KEY}" }
    files = { "file": open(OUTPUT_FILE_NAME, "rb")}
    response1 = requests.post(url, files=files, headers=headers)
    print(response1.status_code)
    response2 = requests.post(f"{ODS_DATASET}/publish/", headers=headers)
    print(response2.status_code)

def main():
    data = []
    issues = collect_issues()
    for issue in issues:
        data.append(parse_issue(issue))
    pd.DataFrame(data).to_csv(OUTPUT_FILE_NAME, index=False)
    ods_sync()

# Main
if __name__ == "__main__":
    main()