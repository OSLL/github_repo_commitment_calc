from github import Github, Repository, GithubException
import csv


EMPTY_FIELD = 'Empty field'


def login(token):
    client = Github(login_or_token=token)
    try:
        client.get_user().login
    except GithubException as err:
        print(f'Github: Connect: error {err.data}')
        raise Exception('Github: Connect: user could not be authenticated please try again.')
    return client


def log_commit_to_csv(info, csv_name):
    fieldnames = ['repository name', 'author name', 'author login', 'author email', 'date and time', 'changed files']
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(info)


def log_commit_to_stdout(info):
    print(info)


def log_repository_commits(repository: Repository, csv_name):
    for commit in repository.get_commits():
        if commit.commit is not None:
            info = {'repository name': repository.full_name,
                    'author name': commit.commit.author.name,
                    'author login': EMPTY_FIELD,
                    'author email': EMPTY_FIELD,
                    'date and time': commit.commit.author.date,
                    'changed files': '; '.join([file.filename for file in commit.files])}

            if commit.author is not None:
                info['author login'] = commit.author.login
                info['author email'] = commit.author.email

            log_commit_to_csv(info, csv_name)
            log_commit_to_stdout(info)


def log_issue_to_csv(info, csv_name):
    fieldnames = ['repository name', 'number', 'title', 'state', 'task', 'created at', 'creator name', 'creator login',
                  'creator email', 'closer name', 'closer login', 'closer email', 'closed at', 'comment body',
                  'comment created at', 'comment author name', 'comment author login', 'comment author email']
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(info)


def log_issue_to_stdout(info):
    print(info)


def log_repository_issues(repository: Repository, csv_name):
    for issue in repository.get_issues(state='all'):
        info_tmp = {
            'repository name': repository.full_name, 'number': issue.number, 'title': issue.title,
            'state': issue.state, 'task': issue.body,
            'created at': issue.created_at,
            'creator name': EMPTY_FIELD,
            'creator login': EMPTY_FIELD,
            'creator email': EMPTY_FIELD,
            'closed at': EMPTY_FIELD,
            'closer name': EMPTY_FIELD,
            'closer login': EMPTY_FIELD,
            'closer email': EMPTY_FIELD,
            'comment body': EMPTY_FIELD,
            'comment created at': EMPTY_FIELD,
            'comment author name': EMPTY_FIELD,
            'comment author login': EMPTY_FIELD,
            'comment author email': EMPTY_FIELD,
            }

        if issue.user is not None:
            info_tmp['creator name'] = issue.user.name
            info_tmp['creator login'] = issue.user.login
            info_tmp['creator email'] = issue.user.email
            info_tmp['creator name'] = issue.user.name
            info_tmp['creator name'] = issue.user.name

        if issue.closed_by is not None:
            info_tmp['closed at'] = issue.closed_at
            info_tmp['creator name'] = issue.closed_by.name
            info_tmp['creator login'] = issue.user.login
            info_tmp['creator email'] = issue.closed_by.email

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


def log_pr_to_csv(info, csv_name):
    fieldnames = ['repository name', 'title', 'state', 'commit into', 'commit from', 'created at', 'creator name', 'creator login', 'creator email',
                  'changed files', 'comment body', 'comment created at', 'comment author name', 'comment author login',
                  'comment author email', 'merger name', 'merger login', 'merger email']
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(info)


def log_pr_to_stdout(info):
    print(info)


def log_repositories_pr(repository: Repository, csv_name):
    for pull in repository.get_pulls(state='all'):
        info_tmp = {
            'repository name': repository.full_name,
            'title': pull.title,
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
            'merger login':  EMPTY_FIELD,
            'merger email': EMPTY_FIELD,
        }

        if pull.merged_by is not None:
            info_tmp['merger name'] = pull.merged_by.name
            info_tmp['merger login'] = pull.merged_by.login
            info_tmp['merger email'] = pull.merged_by.email

        if pull.get_comments().totalCount > 0:
            for comment in pull.get_comments():
                info = info_tmp
                info['comment body'] = comment.body
                info['comment created at'] = comment.created_at
                info['comment author name'] = comment.user.name
                info['comment author login'] = comment.user.login
                info['comment author email'] = comment.user.email
                log_pr_to_csv(info, csv_name)
                log_pr_to_stdout(info)
        else:
            log_pr_to_csv(info_tmp, csv_name)
            log_pr_to_stdout(info_tmp)


def log_repositories(client: Github, repositories, csv_name):
    with open('repos_stats_commits.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'repository name',
                'author name',
                'author login',
                'author email',
                'date and time',
                'changed files',
            )
        )

    with open('repos_stats_issues.csv', 'w', newline='') as file:
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
                'creator email',
                'closer name',
                'closer email',
                'closed at',
                'comment body',
                'comment created at',
                'comment author name',
                'comment author login',
                'comment author email',
            )
        )

    with open('repos_stats_pr.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'repository name',
                'title',
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
            )
        )

    with open(repositories, 'r') as file:
        list_repos = file.read().split('\n')
    for repo_name in list_repos:
        try:
            repo = client.get_repo(repo_name)
        except GithubException as err:
            print(f'Github: Connect: {err.data}')
            raise Exception(f'Github: Connect: failed to load repository {repo_name}')

        log_repository_commits(repo, 'repos_stats_commits.csv')
        log_repository_issues(repo, 'repos_stats_issues.csv')
        log_repositories_pr(repo, 'repos_stats_pr.csv')
