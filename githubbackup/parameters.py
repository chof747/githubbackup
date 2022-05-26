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
