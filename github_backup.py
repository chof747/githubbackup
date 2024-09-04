import os
import re
import textwrap
import time
from typing import Tuple
import requests
import json
import subprocess
from argparse import ArgumentParser
import os
import sys
from dotenv import dotenv_values
from mqtt_logger import MqttLoggingHandler
import logging

PARAMETERS = {
    **dotenv_values(),
    **os.environ
}

MQTTTOPICROOT = "state/githubbackup/TOOL"
ERROR_PREFIX="error"
WARN_PREFIX="warn"
INFO_PREFIX="info"

STATE_STARTED="started"
STATE_FINISHED="finished"

UPTODATE_MESSAGE="Already up to date."

CONNECTION_TIMEOUT_MESSAGE = r"Failed to connect to github\.com port 443 after \d+ ms: Could not connect to server"


cmdLineParser = ArgumentParser(
    description="Backups the git repos of the authenticated user")

cmdLineParser.add_argument('-p', '--path', metavar='path',
                           type=str, help="Path where the repos should be backuped to", required=True)
cmdLineParser.add_argument('-t', '--token', metavar='token',
                           type=str, help="GitHub application token to access RESTFul API", default=PARAMETERS["GITHUBKEY"])
cmdLineParser.add_argument('-v', '--verbose', help="Triggers more verbose logging", action='store_true')

PER_PAGE =25

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

mqttLogHandler = MqttLoggingHandler(PARAMETERS['MQTTSERVER'], 
                                    "log/githubbackup/tool", 
                                    int(PARAMETERS["MQTTPORT"]), 
                                    PARAMETERS["MQTTUSER"], 
                                    PARAMETERS["MQTTPWD"])

mqttLogHandler.setFormatter(logging.Formatter("%(message)s"))
mqttLogHandler.setLevel(logging.INFO)
logger.addHandler(mqttLogHandler)

timout_events = 0
error_events = 0

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

def getInfo(result, repo:str) -> Tuple[str, dict]:
    output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
    
    if (output):
        lines = output.strip().split('\n')

        while ('From' not in lines[0]):
            lines.pop(0)
        lines.pop(0)
        
        updated_branches = []
        for line in lines:
            if not '[up to date]' in line:
                # The updated branch is the second token in such a line
                updated_branch = re.split(r'\s+', line)[-1]
                updated_branches.append(updated_branch)
        
        return (f"{repo} is updated on branches: {', '.join(updated_branches)}" if (updated_branches) else "", {
            'repository' : repo,
            'branches' : updated_branches
        })

    else:
        return ''

def cloneOrUpdateRepo(basePath, repo, url, verbose = False):
    global timout_events
    global error_events

    repoPath = f"{basePath}/{repo}"

    attempts = 3
    step=''

    while attempts > 0:
        try:
            if not os.path.isdir(repoPath):
                step = 'clone'
                result = subprocess.run(['git', 'clone', url, repoPath], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if (verbose):
                    logger.info(f"Added repository {repo}", {
                        'repository' : repo,

                    })
            else:
                # Fetching changes to the repo
                result = None
                step = 'fetch'
                result = subprocess.run(["git", "-C", repoPath, "fetch", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if (verbose):
                    message, details = getInfo(result, repo)
                    if (message): logger.info(message, details)

                # Pulling the data
                result = None
                step = 'pull'
                result = subprocess.run(["git", "-C", repoPath, "pull"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                #we are done and succesfull so break out of the while loop
                break 

        except subprocess.CalledProcessError as e:
            errmsg = e.stderr.decode('utf-8')

            if ((0 < attempts) and (re.search(CONNECTION_TIMEOUT_MESSAGE, errmsg))):
                attempts -= 1;
                timout_events += 1
                time.sleep(5)
            else:
                error_events += 1
                logger.warning(f"Cloning/Updating repo: {repo} failed!", {
                    'repository': repo,
                    'step' : step,
                    'stderr' : errmsg,
                    'rc' : e.returncode
                })
                break

        except Exception as ex:
            error_events += 1
            logger.error("While processing repo: {repo} an unexpected error occured", {
                'exception' : type(ex).__name__,
                'repository': repo,
                'message' : ex,
                'step' : step,
                'stderr' : result.stderr.decode('utf-8') if (result) else None
            })
            break

def main():
    bt : float = time.time()
    mqttLogHandler.connect()

    args = cmdLineParser.parse_args()
    repos = repolist(args.token)
    if (args.verbose):
        logger.info(f"Detected {len(repos)} repositories in GITHUB which will be backuped", {
            'github_count' : len(repos)
        })

    for repo in repos:
        cloneOrUpdateRepo(args.path, repo["name"], repo["clone_url"], args.verbose)

    et : float = time.time()

    logger.info(textwrap.dedent("""\
                Github-Backup Execution summary:
                  execution time = %(exectime).2f s
                  timeout-retries = %(timeout_retries)d
                  error-count = %(error_count)d"""), {
        'exectime' : (et - bt),
        'timeout_retries' : timout_events,
        'error_count' : error_events
    })

    mqttLogHandler.disconnect_mqtt(True)

if __name__ == "__main__":
    main()
