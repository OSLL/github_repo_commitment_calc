import csv
import pytz
import requests
import json
from time import sleep
from git_logger import get_assignee_story
from github import Github, Repository, GithubException, PullRequest
from constants import EMPTY_FIELD, TIMEDELTA, TIMEZONE, PULL_REQUEST_FIELDNAMES, COMMENT_BODY, COMMENT_CREATED_AT, COMMENT_AUTHOR_NAME, COMMENT_AUTHOR_LOGIN, COMMENT_AUTHOR_EMAIL

def log_pr_to_stdout(info):
    print(info)


def log_pr_to_csv(info, csv_name):
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=PULL_REQUEST_FIELDNAMES)
        writer.writerow(info)


def get_related_issues(pull_request_number, repo_owner, repo_name, token):
    access_token = token
    repo_owner = repo_owner.login

    # Формирование запроса GraphQL
    query = """
        {
          repository(owner: "%s", name: "%s") {
            pullRequest(number: %d) {
              id
              closingIssuesReferences(first: 50) {
                edges {
                  node {
                    id
                    body
                    number
                    title
                    url
                  }
                }
              }
            }
          }
        }
        """ % (repo_owner, repo_name, pull_request_number)

    # Формирование заголовков запроса
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Отправка запроса GraphQL
    response = requests.post("https://api.github.com/graphql", headers=headers, data=json.dumps({"query": query}))
    response_data = response.json()
    # Обработка полученных данных
    pull_request_data = response_data["data"]["repository"]["pullRequest"]
    issues_data = pull_request_data["closingIssuesReferences"]["edges"]
    list_issues_url = []
    # сохранение информации об issues
    for issue in issues_data:
        issue_node = issue["node"]
        list_issues_url.append(issue_node["url"])
    return ';'.join(list_issues_url)


def log_repositories_pr(repository: Repository, csv_name, token, start, finish):
    for pull in repository.get_pulls(state='all'):
        if pull.created_at.astimezone(pytz.timezone(TIMEZONE)) < start or pull.created_at.astimezone(
                pytz.timezone(TIMEZONE)) > finish:
            continue
        nvl = lambda val: val or EMPTY_FIELD
        get_info = lambda obj, attr: EMPTY_FIELD if obj is None else getattr(obj, attr)
        pr_data = [repository.full_name, pull.title, pull.number, pull.state, pull.base.label, pull.head.label, pull.created_at,
                   nvl(pull.user.name), pull.user.login, pull.user.email, '; '.join([file.filename for file in pull.get_files()]),
                   EMPTY_FIELD, EMPTY_FIELD, EMPTY_FIELD, EMPTY_FIELD, EMPTY_FIELD, get_info(pull.merged_by, 'name'),
                   get_info(pull.merged_by, 'login'), get_info(pull.merged_by, 'email'), pull.head.ref, pull.base.ref,
                   get_assignee_story(pull), EMPTY_FIELD if pull.issue_url is None else get_related_issues(pull.number, repository.owner, repository.name, token),
                   EMPTY_FIELD if pull.labels is None else ';'.join([label.name for label in pull.labels]), get_info(pull.milestone, 'title')]
        info_tmp = dict(zip(PULL_REQUEST_FIELDNAMES, pr_data))

        if pull.get_comments().totalCount > 0:
            for comment in pull.get_comments():
                info = info_tmp
                info[COMMENT_BODY] = comment.body
                info[COMMENT_CREATED_AT] = comment.created_at
                info[COMMENT_AUTHOR_NAME] = comment.user.name
                info[COMMENT_AUTHOR_LOGIN] = comment.user.login
                info[COMMENT_AUTHOR_EMAIL] = nvl(comment.user.email)
                log_pr_to_csv(info, csv_name)
                log_pr_to_stdout(info)
        else:
            log_pr_to_csv(info_tmp, csv_name)
            log_pr_to_stdout(info_tmp)
        sleep(TIMEDELTA)


def log_pull_requests(client: Github, working_repos, csv_name, token, start, finish, fork_flag):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(PULL_REQUEST_FIELDNAMES)

    for repo in working_repos:
        try:
            print('=' * 20, repo.full_name, '=' * 20)
            log_repositories_pr(repo, csv_name, token, start, finish)
            if fork_flag:
                for forked_repo in repo.get_forks():
                    print('=' * 20, "FORKED:", forked_repo.full_name, '=' * 20)
                    log_repositories_pr(forked_repo, csv_name, token, start, finish)
                    sleep(TIMEDELTA)
            sleep(TIMEDELTA)
        except Exception as e:
            print(e)
