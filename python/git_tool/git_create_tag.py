# -*- coding: utf-8 -*-
#!/usr/bin/python
##-------------------------------------------------------------------
## @copyright 2017 DennyZhang.com
## Licensed under MIT
##   https://raw.githubusercontent.com/DennyZhang/devops_public/master/LICENSE
##
## File : git_create_tag.py
## Author : Denny <denny@dennyzhang.com>
## Description : Create monthly git tag for all repos in your projects
## Dependency:
##        pip install GitPython
##
## Sample:
##        python git_create_tag.py --tag_name "2017-08-01" --delete_tag_already_exists \
##               --git_list_file "/tmp/git_list.txt"
##
##        Sample of git_list_file
##                   git@bitbucket.org:dennyzhang/devops.git
##                   git@bitbucket.org:dennyzhang/frontend.git
##                   git@bitbucket.org:dennyzhang/backend.git
## --
## Created : <2017-03-24>
## Updated: Time-stamp: <2017-05-20 00:12:12>
##-------------------------------------------------------------------
import os, sys
import logging
import argparse

import datetime
# Install package first: pip install GitPython
import git

log_file = "/var/log/%s.log" % (os.path.basename(__file__).rstrip('\.py'))
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())

def get_repo_name(repo_url):
    # https://github.com/DennyZhang/devops_public.git -> devops_public
    # git@github.com:DennyZhang/devops_public.git -> devops_public
    l = repo_url.split(".")
    return l[-2].split("/")[-1]

# TODO: git passphrase
def git_create_tag(git_repo, tag_name, delete_tag_already_exists):
    # https://gitpython.readthedocs.io/en/stable/tutorial.html#meet-the-repo-type
    if tag_name in git_repo.tags:
        if delete_tag_already_exists is True:
            logging.info("Tag(%s) already exists, delete it first. Git repo: %s" % \
                         (tag_name, git_repo.working_dir))
            git_repo.delete_tag(tag_name)
            git_repo.git.execute(["git", "push", "--delete", "origin", tag_name])
        else:
            logging.warn("Tag(%s) already exists, skip current process.")
            return True

    # TODO: check return code
    logging.info("Create local tag(%s)" % (tag_name))
    git_repo.create_tag(tag_name, message = "Automatically create git tag.")
    logging.info("Push local tag(%s) to remote" % (tag_name))
    git_repo.remotes.origin.push(tag_name)
    return True

def git_list_create_tag(working_dir, git_list_file, tag_name, delete_tag_already_exists):
    git_list = []
    with open(git_list_file,'r') as f:
        for row in f:
            row = row.strip()
            if row == "" or row.startswith('#'):
                continue
            git_list.append(row)

    for repo_url in git_list:
        # TODO: re-use current code folder
        code_dir = "%s/%s" % (working_dir, get_repo_name(repo_url))
        git_repo = git.Repo.clone_from(repo_url, code_dir)
        git_create_tag(git_repo, tag_name, delete_tag_already_exists)
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
##        python git_create_tag.py -tag_name "2017-08-01" --delete_tag_already_exists \
##               --git_list_file /tmp/git_list.txt"
    parser.add_argument('--tag_name', required=False, default=datetime.datetime.utcnow().strftime("%Y-%m-%d"), \
                        help="What tag name to create for git repos", type=str)
    parser.add_argument('--git_list_file', required=False, default="", \
                        help="The file should specify a list of git repos", type=str)
    parser.add_argument('--delete_tag_already_exists', dest='delete_tag_already_exists', \
                        action='store_true', default=False, \
                        help="If enabled, we will delete existing tag if it already exists")
    parser.add_argument('--working_dir', required=False, default="/tmp", \
                        help="Working directory for creating git tags", type=str)

    l = parser.parse_args()
    tag_name = l.tag_name
    delete_tag_already_exists = l.delete_tag_already_exists
    git_list_file = l.git_list_file
    working_dir = l.working_dir

    if git_list_create_tag(working_dir, git_list_file, tag_name, delete_tag_already_exists) is True:
        logging.info("OK: Action is done successfully.")
        sys.exit(0)
    else:
        logging.error("ERROR: Action has failed.")
        sys.exit(0)
## File : git_create_tag.py ends