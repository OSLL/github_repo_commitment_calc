import csv
import pytz
import requests
import json
from time import sleep
from github import Github, Repository, GithubException, PullRequest

EMPTY_FIELD = 'Empty field'
timedelta = 0.05
timezone = 'Europe/Moscow'
fieldnames = ('repository name', 'number', 'title', 'state', 'task', 'created at', 'creator name', 'creator login',
              'creator email', 'closer name', 'closer login', 'closer email', 'closed at', 'comment body',
              'comment created at', 'comment author name', 'comment author login', 'comment author email',
              'assignee story', 'connected pull requests', 'labels', 'milestone')

def log_issue_to_csv(info, csv_name):
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
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

def get_assignee_story(github_object):
    assignee_result = ""
    events = github_object.get_issue_events() if type(
        github_object) is PullRequest.PullRequest else github_object.get_events()
    for event in events:
        if event.event == "assigned" or event.event == "unassigned":
            date = event.created_at
            if event.event == "assigned":
                assigner = github_object.user.login
                assignee = event.assignee.login
                assignee_result += f"{date}: {assigner} -> {assignee}; "
            else:
                assigner = github_object.user.login
                assignee = event.assignee.login
                assignee_result += f"{date}: {assigner} -/> {assignee}; "
        sleep(timedelta)
    return assignee_result

def log_repository_issues(repository: Repository, csv_name, token, start, finish):
    for issue in repository.get_issues(state='all'):
        if issue.created_at.astimezone(pytz.timezone(timezone)) < start or issue.created_at.astimezone(
                pytz.timezone(timezone)) > finish:
            continue
        info_tmp = {
            'repository name': repository.full_name, 'number': issue.number, 'title': issue.title,
            'state': issue.state, 'task': issue.body,
            'created at': issue.created_at,
            'creator name': EMPTY_FIELD,
            'creator login': EMPTY_FIELD,
            'creator email': EMPTY_FIELD if issue.user.email is None else issue.user.email,
            'closed at': EMPTY_FIELD,
            'closer name': EMPTY_FIELD,
            'closer login': EMPTY_FIELD,
            'closer email': EMPTY_FIELD if issue.closed_by is None else issue.closed_by.email,
            'comment body': EMPTY_FIELD,
            'comment created at': EMPTY_FIELD,
            'comment author name': EMPTY_FIELD,
            'comment author login': EMPTY_FIELD,
            'comment author email': EMPTY_FIELD,
            'assignee story': EMPTY_FIELD,
            'connected pull requests': EMPTY_FIELD,
            'labels': EMPTY_FIELD if issue.labels is None else ';'.join([label.name for label in issue.labels]),
            'milestone': EMPTY_FIELD if issue.milestone is None else issue.milestone.title
        }

        if issue.number is not None:
            info_tmp['connected pull requests'] = get_connected_pulls(issue.number, repository.owner, repository.name,
                                                                      token)

        info_tmp['assignee story'] = get_assignee_story(issue)

        if issue.user is not None:
            info_tmp['creator name'] = issue.user.name
            info_tmp['creator login'] = issue.user.login

        if issue.closed_by is not None:
            info_tmp['closed at'] = issue.closed_at
            info_tmp['closer name'] = issue.closed_by.name
            info_tmp['closer login'] = issue.user.login

        if issue.get_comments().totalCount > 0:
            for comment in issue.get_comments():
                info = info_tmp
                info['comment body'] = comment.body
                info['comment created at'] = comment.created_at
                info['comment author name'] = comment.user.name
                info['comment author login'] = comment.user.login
                info['comment author email'] = comment.user.email
                log_issue_to_csv(info, csv_name)
                log_issue_to_stdout(info)
        else:
            log_issue_to_csv(info_tmp, csv_name)
            log_issue_to_stdout(info_tmp)
        sleep(timedelta)


def log_issues(client: Github, working_repo, csv_name, token, start, finish, fork_flag):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)

    for repo in working_repo:
        try:
            print('=' * 20, repo.full_name, '=' * 20)
            log_repository_issues(repo, csv_name, token, start, finish)
            if fork_flag:
                for forked_repo in repo.get_forks():
                    print('=' * 20, "FORKED:", forked_repo.full_name, '=' * 20)
                    log_repository_issues(forked_repo, csv_name, token, start, finish)
                    sleep(timedelta)
            sleep(timedelta)
        except Exception as e:
            print(e)
