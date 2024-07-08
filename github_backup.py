import os
import re
import requests
import json
import subprocess
from argparse import ArgumentParser
import os
from dotenv import dotenv_values

PARAMETERS = {
    **dotenv_values(),
    **os.environ
}

cmdLineParser = ArgumentParser(
    description="Backups the git repos of the authenticated user")

cmdLineParser.add_argument('-p', '--path', metavar='path',
                           type=str, help="Path where the repos should be backuped to", required=True)
cmdLineParser.add_argument('-t', '--token', metavar='token',
                           type=str, help="GitHub application token to access RESTFul API", default=PARAMETERS["GITHUBKEY"])
cmdLineParser.add_argument('-v', '--verbose', help="Triggers more verbose logging", action='store_true')


PER_PAGE =25

def extract_relevant_info(repo, apikey):

    #print(repo["clone_url"])
    #print(re.match("(https?\:\/\/)(.*)", repo["clone_url"]))
    return {
        "name" : repo["name"],
        "clone_url" : re.sub("(https?://)(.*)", f'\\1{apikey}@\\2', repo["clone_url"])
    }

def repolist(apikey):
    
    repos = []
    page = 1

    while True:
        response = requests.get(f"https://api.github.com/user/repos?page={page}&per_page={PER_PAGE}", headers={
            "Authorization" : f'token {apikey}'
        })

        if (200 == response.status_code):
    
            pageresult = json.loads(response.text)
            repos.extend([extract_relevant_info(r, apikey) for r in pageresult])

            if len(pageresult)<PER_PAGE:
                break;
            else:
                page = page + 1
        else:
            print(f"Error received: {response.status_code}, {response.text}")
            exit()

    return repos

def cloneOrUpdateRepo(basePath, repo, url):
    repoPath = f"{basePath}/{repo}"
    if (not os.path.isdir(repoPath)):
        subprocess.run(['git', 'clone', '-q', url, repoPath])
    subprocess.run(["git", "-C", repoPath, "pull", "--all", "-q"])

def main():
    args = cmdLineParser.parse_args()
    repos = repolist(args.token)
    print(f"You have: {len(repos)} repositories in GITHUB start cloning ...")
    
    for repo in repos:
        verbose_logging = repo["clone_url"] if args.verbose else ""
        print(f'cloning/updating repo: {repo["name"]} {verbose_logging}')
        
        cloneOrUpdateRepo(args.path, repo["name"], repo["clone_url"])

if __name__ == "__main__":
    main()
