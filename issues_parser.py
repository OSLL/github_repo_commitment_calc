import csv
import pytz
import requests
import json
from time import sleep
from git_logger import get_assignee_story
from github import Github, Repository, GithubException, PullRequest
from constants import EMPTY_FIELD, TIMEDELTA, TIMEZONE, ISSUE_FIELDNAMES, COMMENT_BODY, COMMENT_CREATED_AT, COMMENT_AUTHOR_NAME, COMMENT_AUTHOR_LOGIN, COMMENT_AUTHOR_EMAIL

def log_issue_to_csv(info, csv_name):
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=ISSUE_FIELDNAMES)
        writer.writerow(info)


def log_issue_to_stdout(info):
    print(info)


def get_connected_pulls(issue_number, repo_owner, repo_name, token):
    access_token = token
    repo_owner = repo_owner.login
    # Формирование запроса GraphQL
    query = """
    {
      repository(owner: "%s", name: "%s") {
        issue(number: %d) {
          timelineItems(first: 50, itemTypes:[CONNECTED_EVENT,CROSS_REFERENCED_EVENT]) {
            filteredCount
            nodes {
              ... on ConnectedEvent {
                ConnectedEvent: subject {
                  ... on PullRequest {
                    number
                    title
                    url
                  }
                }
              }
              ... on CrossReferencedEvent {
                CrossReferencedEvent: source {
                  ... on PullRequest {
                    number
                    title
                    url
                  }
                }
              }
            }
          }
        }
      }
    }""" % (repo_owner, repo_name, issue_number)

    # Формирование заголовков запроса
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Отправка запроса GraphQL
    response = requests.post("https://api.github.com/graphql", headers=headers, data=json.dumps({"query": query}))
    response_data = response.json()
    # Обработка полученных данных
    pull_request_data = response_data["data"]["repository"]["issue"]
    list_url = []
    if (pull_request_data is not None):
        issues_data = pull_request_data["timelineItems"]["nodes"]
        for pulls in issues_data:
            if (pulls.get("CrossReferencedEvent") != None and pulls.get("CrossReferencedEvent").get(
                    "url") not in list_url):
                list_url.append(pulls.get("CrossReferencedEvent").get("url"))
            if (pulls.get("ConnectedEvent") != None and pulls.get("ConnectedEvent").get("url") not in list_url):
                list_url.append(pulls.get("ConnectedEvent").get("url"))
        if (list_url == []):
            return 'Empty field'
        else:
            return ';'.join(list_url)
    return 'Empty field'


def log_repository_issues(repository: Repository, csv_name, token, start, finish):
    for issue in repository.get_issues(state='all'):
        if issue.created_at.astimezone(pytz.timezone(TIMEZONE)) < start or issue.created_at.astimezone(
                pytz.timezone(TIMEZONE)) > finish:
            continue
        nvl = lambda val: val or EMPTY_FIELD
        get_info = lambda obj, attr: EMPTY_FIELD if obj is None else getattr(obj, attr)
        issue_data = [repository.full_name, issue.number, issue.title, issue.state, issue.body, issue.created_at, get_info(issue.user, 'name'),
                      get_info(issue.user, 'login'), get_info(issue.user, 'email'), nvl(issue.closed_at), get_info(issue.closed_by, 'name'),
                      get_info(issue.closed_by, 'login'), get_info(issue.closed_by, 'email'), EMPTY_FIELD, EMPTY_FIELD, EMPTY_FIELD, EMPTY_FIELD,
                      EMPTY_FIELD, get_assignee_story(issue), EMPTY_FIELD if issue.number is None else get_connected_pulls(issue.number, repository.owner, repository.name, token),
                      EMPTY_FIELD if issue.labels is None else ';'.join([label.name for label in issue.labels]), get_info(issue.milestone, 'title')]
        info_tmp = dict(zip(ISSUE_FIELDNAMES, issue_data))

        if issue.get_comments().totalCount > 0:
            for comment in issue.get_comments():
                info = info_tmp
                info[COMMENT_BODY] = comment.body
                info[COMMENT_CREATED_AT] = comment.created_at
                info[COMMENT_AUTHOR_NAME] = comment.user.name
                info[COMMENT_AUTHOR_LOGIN] = comment.user.login
                info[COMMENT_AUTHOR_EMAIL] = nvl(comment.user.email)
                log_issue_to_csv(info, csv_name)
                log_issue_to_stdout(info)
        else:
            log_issue_to_csv(info_tmp, csv_name)
            log_issue_to_stdout(info_tmp)
        sleep(TIMEDELTA)


def log_issues(client: Github, working_repo, csv_name, token, start, finish, fork_flag):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(ISSUE_FIELDNAMES)

    for repo in working_repo:
        try:
            print('=' * 20, repo.full_name, '=' * 20)
            log_repository_issues(repo, csv_name, token, start, finish)
            if fork_flag:
                for forked_repo in repo.get_forks():
                    print('=' * 20, "FORKED:", forked_repo.full_name, '=' * 20)
                    log_repository_issues(forked_repo, csv_name, token, start, finish)
                    sleep(TIMEDELTA)
            sleep(TIMEDELTA)
        except Exception as e:
            print(e)
