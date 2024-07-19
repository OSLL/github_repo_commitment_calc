import csv
import pytz
import requests
import json
from time import sleep
from github import Github, Repository, GithubException, PullRequest

EMPTY_FIELD = 'Empty field'
timedelta = 0.05
timezone = 'Europe/Moscow'
fieldnames = ('repository name', 'title', 'id', 'state', 'commit into', 'commit from', 'created at', 'creator name',
              'creator login', 'creator email', 'changed files', 'comment body',
              'comment created at', 'comment author name', 'comment author login',
              'comment author email', 'merger name', 'merger login', 'merger email', 'source branch',
              'target branch', 'assignee story', 'related issues', 'labels', 'milestone')

def log_pr_to_stdout(info):
    print(info)
def log_pr_to_csv(info, csv_name):
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
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

def log_repositories_pr(repository: Repository, csv_name, token, start, finish):
    for pull in repository.get_pulls(state='all'):
        if pull.created_at.astimezone(pytz.timezone(timezone)) < start or pull.created_at.astimezone(
                pytz.timezone(timezone)) > finish:
            continue
        info_tmp = {
            'repository name': repository.full_name,
            'title': pull.title,
            'id': pull.number,
            'state': pull.state,
            'commit into': pull.base.label,
            'commit from': pull.head.label,
            'created at': pull.created_at,
            'creator name': EMPTY_FIELD if pull.user.name is None else pull.user.name,
            'creator login': pull.user.login,
            'creator email': pull.user.email,
            'changed files': '; '.join([file.filename for file in pull.get_files()]),
            'comment body': EMPTY_FIELD,
            'comment created at': EMPTY_FIELD,
            'comment author name': EMPTY_FIELD,
            'comment author login': EMPTY_FIELD,
            'comment author email': EMPTY_FIELD,
            'merger name': EMPTY_FIELD,
            'merger login': EMPTY_FIELD,
            'merger email': EMPTY_FIELD,
            'source branch': pull.head.ref,
            'target branch': pull.base.ref,
            'assignee story': EMPTY_FIELD,
            'related issues': EMPTY_FIELD,
            'labels': EMPTY_FIELD if pull.labels is None else ';'.join([label.name for label in pull.labels]),
            'milestone': EMPTY_FIELD if pull.milestone is None else pull.milestone.title
        }
        if pull.issue_url is not None:
            info_tmp['related issues'] = get_related_issues(pull.number, repository.owner, repository.name,
                                                            token)

        if pull.merged_by is not None:
            info_tmp['merger name'] = pull.merged_by.name
            info_tmp['merger login'] = pull.merged_by.login
            info_tmp['merger email'] = pull.merged_by.email

        info_tmp['assignee story'] = get_assignee_story(pull)

        if pull.get_comments().totalCount > 0:
            for comment in pull.get_comments():
                info = info_tmp
                info['comment body'] = comment.body
                info['comment created at'] = comment.created_at
                info['comment author name'] = comment.user.name
                info['comment author login'] = comment.user.login
                info['comment author email'] = EMPTY_FIELD if comment.user.email is None else comment.user.email
                log_pr_to_csv(info, csv_name)
                log_pr_to_stdout(info)
        else:
            log_pr_to_csv(info_tmp, csv_name)
            log_pr_to_stdout(info_tmp)
        sleep(timedelta)

def log_pull_requests(client: Github, working_repos, csv_name, token, start, finish, fork_flag):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)

    for repo in working_repos:
        try:
            print('=' * 20, repo.full_name, '=' * 20)
            log_repositories_pr(repo, csv_name, token, start, finish)
            if fork_flag:
                for forked_repo in repo.get_forks():
                    print('=' * 20, "FORKED:", forked_repo.full_name, '=' * 20)
                    log_repositories_pr(forked_repo, csv_name, token, start, finish)
                    sleep(timedelta)
            sleep(timedelta)
        except Exception as e:
            print(e)
