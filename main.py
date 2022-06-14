#!/bin/python3
# usage: python3 main.py --token <token> --repos <repos_file>
import argparse
from github import Github
import csv


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, required=True, help='token github account')
    parser.add_argument('-l', '--list', type=str, required=True, help='repos names file')
    return parser.parse_args()


def get_commits_info(repo):
    commits = []
    for commit in repo.get_commits():
        info = {'name': commit.commit.author.name, 'email': commit.commit.author.email,
                'date': commit.commit.author.date.ctime(), 'files': [file.filename for file in commit.files]}
        commits.append(info)
        if len(commits) > 3:
            return commits
    return commits


def write_commits(token, list_path):
    name_csv = 'repos_stats.csv'
    with open(name_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Название репозитория',
                'Логин',
                'Почта',
                'Дата Время',
                'Список затронутых файлов'
            )
        )

    list_repos = []
    with open(list_path, 'r') as file:
        list_repos = file.read().split('\n')

    git = Github(login_or_token=token)
    for repo_name in list_repos:
        try:
            repo = git.get_repo(repo_name)
        except Exception:
            print(f'{repo_name} not found!')
        else:
            commits = get_commits_info(repo)
            for commit in commits:
                author_name, email, date, files = commit.values()
                files = ', '.join(files)
                print(f'{repo_name}: {author_name}, {email}, {date}, {files}')

                with open(name_csv, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        (
                            repo_name,
                            author_name,
                            email,
                            date,
                            files
                        )
                    )


if __name__ == '__main__':
    args = parse_args()
    write_commits(token=args.token, list_path=args.list)
