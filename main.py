import subprocess
import re

"""
Scans a repo and gets the branches and latest commit id of each branch
"""
def get_branches(remote_url: str) -> dict[str,str]:
    output = subprocess.check_output(['git', 'ls-remote', '--heads', remote_url]).decode('ascii')

    branches = {}
    for line in output.split('\n')[:-1]:  # [:-1] is because the last line is blank
        commit_id, ref = line.split()
        branches[ref[11:]] = commit_id  # First 11 charecters are 'refs/heads/'

    return branches


"""
Takes a list of strings and filters out the ones that can't be used as part of a domain name
"""
def branch_to_zone_names(branches: dict[str,str]) -> dict[str,str]:

    valid = {}
    invalid = {}
    transformed = {}

    # Split the vaild and invalid names into their own list
    for branch, commit_id in branches.items():
        if re.match('^[a-z0-9]+([a-z0-9-][a-z0-9])*$', branch):
            valid[branch] = commit_id
        else:
            invalid[branch] = commit_id
    
    # Trys to transform some of the invalid names into valid names
    for branch, commit_id in invalid.items():
        new_name = branch.lower().replace('_', '-').replace('/', '-')
        new_name = re.sub(r'[^a-z0-9-]', 'x', new_name)
        new_name = re.sub(r'-{2,}', '-', new_name)
        new_name = new_name.strip('-')

        if new_name not in valid:
            transformed[new_name] = commit_id
    
    return valid | transformed
            

"""
Deploys an environment
"""
def deploy_env(app_name, branch_name, commit_id, namespace) -> None:
    pass


"""
Scans a Git repo and deploys an environment all the branches it can.
"""
def update_app(app_name, remote_url) -> None:
    branches = get_branches(remote_url)

    for branch in filter_names(branches.keys()):
        deploy_env(app_name, branch, branches[branch])
    
    # TODO: remove environments if corresponding branch was deleted


# Pseudocode phase 1:
# reads a config file that conains all the apps.
# while true: 
#   for each app: update_app()
#   wait 5 mins

# Pseudocode phase 2:
# while true:
#    Read all CRD for app
#    for each app: update_app()
#    wait 5 mins

# Phase 3: Phase 2 plus a webhook for faster updating. Similar to FluxCD

# 