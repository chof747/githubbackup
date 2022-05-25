# Requirements

1. obtain the list of repositories of a user (public and private)
2. clone all these repositories into a local backup directory
3. regularly update the changes by pulling the repositories into that directory

# Solution Concept

## Summary
The backup utility will obtain the list of repositories of a specific user from github with an API key and is then 
cloning and pulling the requirements into the backup directory.

The idea is to have this packaged in a docker container which has the backup directory mounted to a specific location, 
executes the utility and exits. By this it can be deployed on any server and there run as a scheduled job by running
the docker container

## Technical Implementation

 - The utility will be implemented as a python tool
 - Interaction with Github to obtain the list of repositories happens via the github API and the `requests` library
 - Cloning the repos and pulling changes will be done via `system` calls to the `git` command line client

### Requirements:

 - Python libraries: python-dotenv, requests
 - Git command line client
 - Docker (for deployment)

## Solution Components
