import csv
import requests
import json
import pytz

from github import Github, Repository, GithubException, PullRequest

EMPTY_FIELD = 'Empty field'
timedelta = 0.05
timezone = 'Europe/Moscow'


def login(token):
    client = Github(login_or_token=token)

    try:
        client.get_user().login
    except GithubException as err:
        print(f'Github: Connect: error {err.data}')
        print('Github: Connect: user could not be authenticated please try again.')
        raise exit(1)
    else:
        return client


def get_next_repo(client: Github, repositories):
    with open(repositories, 'r') as file:
        list_repos = [x for x in file.read().split('\n') if x]
    print(list_repos)
    for repo_name in list_repos:
        try:
            repo = client.get_repo(repo_name)
        except GithubException as err:
            print(f'Github: Connect: error {err.data}')
            print(f'Github: Connect: failed to load repository "{repo_name}"')
            exit(1)
        else:
            yield repo


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


def log_commit_to_csv(info, csv_name):
    fieldnames = ['repository name', 'commit id', 'author name', 'author login', 'author email', 'date and time',
                  'changed files']
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(info)


def log_commit_to_stdout(info):
    print(info)


def log_repository_commits(repository: Repository, csv_name, start, finish):
    for commit in repository.get_commits():
        if commit.commit.author.date.astimezone(
                pytz.timezone(timezone)) < start or commit.commit.author.date.astimezone(
                pytz.timezone(timezone)) > finish:
            continue
        if commit.commit is not None:
            info = {'repository name': repository.full_name,
                    'author name': commit.commit.author.name,
                    'author login': EMPTY_FIELD,
                    'author email': EMPTY_FIELD,
                    'date and time': commit.commit.author.date,
                    'changed files': '; '.join([file.filename for file in commit.files]),
                    'commit id': commit.commit.sha}

            if commit.author is not None:
                info['author login'] = commit.author.login

            if commit.commit.author is not None:
                info['author email'] = commit.commit.author.email

            log_commit_to_csv(info, csv_name)
            log_commit_to_stdout(info)
            sleep(timedelta)


def log_issue_to_csv(info, csv_name):
    fieldnames = ['repository name', 'number', 'title', 'state', 'task', 'created at', 'creator name', 'creator login',
                  'creator email', 'closer name', 'closer login', 'closer email', 'closed at', 'comment body',
                  'comment created at', 'comment author name', 'comment author login', 'comment author email',
                  'assignee story', 'connected pull requests']

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
            if (pulls.get("CrossReferencedEvent") != None and pulls.get("CrossReferencedEvent").get("url") not in list_url) :
                list_url.append(pulls.get("CrossReferencedEvent").get("url"))
            if (pulls.get("ConnectedEvent") != None and pulls.get("ConnectedEvent").get("url") not in list_url):
                list_url.append(pulls.get("ConnectedEvent").get("url"))
        if (list_url == []):
            return 'Empty field'
        else:
            return list_url
    return 'Empty field'
    

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
            'connected pull requests': EMPTY_FIELD
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


def log_pr_to_csv(info, csv_name):
    fieldnames = ['repository name', 'title', 'id', 'state', 'commit into', 'commit from', 'created at', 'creator name',
                  'creator login', 'creator email',
                  'changed files', 'comment body', 'comment created at', 'comment author name', 'comment author login',
                  'comment author email', 'merger name', 'merger login', 'merger email', 'source branch',
                  'target branch', 'assignee story', 'related issues']
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(info)


def log_pr_to_stdout(info):
    print(info)


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
    return list_issues_url
    

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
            'related issues': EMPTY_FIELD
        }
        if pull.issue_url is not None:
            info_tmp['related issues'] = get_related_issues(pull.number, repository.owner, repository.name, token)

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


def log_pull_requests(client: Github, repositories, csv_name, token, start, finish):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'repository name',
                'title',
                'id',
                'state',
                'commit into',
                'commit from',
                'created at',
                'creator name',
                'creator login',
                'creator email',
                'changed files',
                'comment body',
                'comment created at',
                'comment author name',
                'comment author login',
                'comment author email',
                'merger name',
                'merger login',
                'merger email',
                'source branch',
                'target branch',
                'related issues'
                'assignee story',
                'related issues'
            )
        )

    for repo in get_next_repo(client, repositories):

        try:
            log_repositories_pr(repo, csv_name, tokrn, start, finish)
            sleep(timedelta)
        except e:
            print(e)


def log_issues(client: Github, repositories, csv_name, token, start, finish):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'repository name',
                'number',
                'title',
                'state',
                'task',
                'created at',
                'creator name',
                'creator login',
                'creator email',
                'closer name',
                'closer login',
                'closer email',
                'closed at',
                'comment body',
                'comment created at',
                'comment author name',
                'comment author login',
                'comment author email',
                'connected pull requests'
                'assignee story',
                'connected pull requests'
            )
        )

    for repo in get_next_repo(client, repositories):

        try:
            log_repository_issues(repo, csv_name, token, start, finush)
            sleep(timedelta)
        except e:
            print(e)


def log_commits(client: Github, repositories, csv_name, start, finish):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'repository name',
                'author name',
                'author login',
                'author email',
                'date and time',
                'changed files',
                'commit id'
            )
        )

    for repo in get_next_repo(client, repositories):

        try:
            log_repository_commits(repo, csv_name, starr, finish)
            sleep(timedelta)
        except e:
            print(e)
