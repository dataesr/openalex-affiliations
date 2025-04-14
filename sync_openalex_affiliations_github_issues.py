#!/usr/bin/env python3
# Execution example: python3 sync_openalex_affiliations_github_issues.py

# Imports
from dotenv import load_dotenv
import os
import pandas as pd
import re
import requests

load_dotenv()

# Config
GIT_PER_PAGE = 100
GIT_REPOSITORY_NAME = "dataesr/openalex-affiliations"
ODS_DATASET = "https://data.enseignementsup-recherche.gouv.fr/api/automation/v1.0/datasets/da_lyihp9"
ODS_FILE_ID = "re_agmowf"
OUTPUT_FILE_NAME = "github_issues.csv"


try:
    GIT_TOKEN = os.environ["GIT_TOKEN"]
    GIT_USERNAME = os.environ["GIT_USERNAME"]
    ODS_API_KEY = os.environ["ODS_API_KEY"]
except KeyError:
    print("Some config is not defined !")


# Functions
def collect_issues() -> list[dict]:
    all_issues = []
    pages_remaining = True
    url = f"https://api.github.com/repos/{GIT_REPOSITORY_NAME}/issues?per_page={GIT_PER_PAGE}&state=all"
    gh_session = requests.Session()
    gh_session.auth = (GIT_USERNAME, GIT_TOKEN)
    while pages_remaining:
        response = gh_session.get(url)
        link = response.headers.get("link")
        pages_remaining = link and 'rel="next"' in link
        issues = response.json()
        if isinstance(issues, list):
            all_issues += issues
        if pages_remaining:
            matches = re.search(r"(?<=<)([\S]*)(?=>; rel=\"next\")", link)
            url = matches.group(0)
    return all_issues


def parse_issue(issue:dict) -> dict:
    body = issue["body"]
    new_elt = {}
    new_elt["github_issue_id"] = issue["number"]
    new_elt["github_issue_link"] = f"https://github.com/{GIT_REPOSITORY_NAME}/issues/{issue['number']}"
    new_elt["state"] = issue["state"]
    new_elt["date_opened"] = issue["created_at"][0:10]
    new_elt["date_closed"] = None if issue["closed_at"] is None else issue["closed_at"][0:10]
    a = "\nraw_affiliation_name: "
    b = "\nnew_rors: "
    c = "\nprevious_rors: "
    d = "\nworks_examples: "
    e = "\nsearched between: "
    f = "\ncontact: "
    g = "\nversion: "
    a_start = body.find(a) + len(a)
    a_end = body.find(b)
    b_start = a_end + len(b)
    b_end = body.find(c)
    c_start = b_end + len(c)
    c_end = body.find(d)
    d_start = c_end + len(d)
    d_end = body.find(e)
    e_start = d_end + len(e)
    e_end = body.find(f)
    f_start = e_end + len(f)
    f_end = body.find(g)
    g_start = f_end + len(g)
    g_end = len(body)
    new_elt["raw_affiliation_name"] = body[a_start:a_end].replace("\r", "")
    new_rors = [r.replace("\r", "") for r in body[b_start:b_end].split(";") if r]
    previous_rors = [r.replace("\r", "") for r in body[c_start:c_end].split(";") if r]
    added_rors = list(set(new_rors) - set(previous_rors))
    removed_rors = list(set(previous_rors) - set(new_rors))
    openalex_works_examples = [f"https://api.openalex.org/works/{work}" for work in body[d_start:d_end].replace("\r", "").split(";")]
    searched_between = body[e_start:e_end]
    new_elt["has_added_rors"] = 1 if len(added_rors) > 0 else 0
    new_elt["has_removed_rors"] = 1 if len(removed_rors) > 0 else 0
    new_elt["new_rors"] = ";".join(new_rors)
    new_elt["previous_rors"] = ";".join(previous_rors)
    new_elt["added_rors"] = ";".join(added_rors)
    new_elt["removed_rors"] = ";".join(removed_rors)
    new_elt["openalex_works_examples"] = ";".join(openalex_works_examples)
    new_elt["searched_between"] = searched_between
    new_elt["contact"] = body[f_start:f_end].replace("\r", "").lower()
    if "@" in new_elt["contact"]:
        new_elt["contact_domain"] = new_elt["contact"].split("@")[1].strip().replace("\r", "")
    new_elt["version"] = body[g_start:g_end]
    return new_elt


def ods_sync():
    url = f"{ODS_DATASET}/resources/files/"
    headers = { "Authorization": f"apikey {ODS_API_KEY}" }
    files = { "file": open(OUTPUT_FILE_NAME, "rb")}
    response = requests.post(url, files=files, headers=headers)
    json = {
        "datasource": { "type": "uploaded_file", "file": { "uid": response.json().get("uid") } },
        "title": OUTPUT_FILE_NAME,
        "type": "csvfile",
    }
    requests.put(f"{ODS_DATASET}/resources/{ODS_FILE_ID}/", headers=headers, json=json)
    requests.post(f"{ODS_DATASET}/publish/", headers=headers)


def main():
    data = []
    issues = collect_issues()
    for issue in issues:
        parsed_issue = parse_issue(issue)
        data.append(parsed_issue)
    pd.DataFrame(data).to_csv(OUTPUT_FILE_NAME, index=False)
    ods_sync()
    os.remove(OUTPUT_FILE_NAME)


# Main
if __name__ == "__main__":
    main()