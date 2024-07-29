from git import Repo, exc
import os
import time
import csv
from constants import WIKI_FIELDNAMES, EMPTY_FIELD, EMPTY_TREE_SHA, ACTIVITY, AUTHOR_LOGIN, PAGE, ACTION

def log_wiki_to_csv(info, csv_name):
    with open(csv_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=WIKI_FIELDNAMES)
        writer.writerow(info)


def wikiparser(client, repositories, path_drepo, csv_name):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(WIKI_FIELDNAMES)

    #Создаем список репозиториев из файла
    with open(repositories, 'r') as file:
        list_repos = [x for x in file.read().split('\n') if x]
    error_repos = []

    data_changes = []
    for name_rep in list_repos:
        #Проверяем, есть ли репозиторий в папке
        dir_path = path_drepo + "/" + name_rep
        if os.path.exists(dir_path):
            #Обновляем репозиторий
            if len(os.listdir(dir_path)) > 0:
                repo = Repo(dir_path)
                repo.remotes.origin.pull()
            else:
                os.rmdir(dir_path)
                error_repos.append(name_rep)
                continue
        else:
            #Клонируем репозиторий в папку
            dir_path = path_drepo + "/" + name_rep
            os.makedirs(dir_path, exist_ok=True)
            repo_url = f"git@github.com:{name_rep}.wiki.git"
            try:
                repo = Repo.clone_from(repo_url, dir_path)
            except exc.GitCommandError:
                os.rmdir(dir_path)
                error_repos.append(name_rep)
                continue

        print("=" * 20, name_rep, "=" * 20)
        #Вывод изменений
        wiki_commits = repo.iter_commits(all=True)
        for commit in wiki_commits:
            data_commit = dict()
            parent = commit.parents
            commit_data = [name_rep, commit.author, EMPTY_FIELD, time.strftime("%Y-%m-%d %H:%M:%S%z", time.gmtime(commit.committed_date)),
                           EMPTY_FIELD, commit, commit.stats.total["insertions"], commit.stats.total["deletions"]]
            info = dict(zip(WIKI_FIELDNAMES, commit_data))
            if commit.author.email and len(commit.author.email.split('+')) > 1:
                data_commit[AUTHOR_LOGIN] = commit.author.email.split('+')[1].split('@users')[0]
            if parent:
                data_commit[PAGE] = ';'.join([diff.b_path for diff in parent[0].diff(commit)])
                data_commit[ACTION] = ';'.join([ACTIVITY[diff.change_type] for diff in parent[0].diff(commit)])
            else:
                #Первый коммит
                data_commit[PAGE] = ';'.join([diff.b_path for diff in commit.diff(EMPTY_TREE_SHA)])
                data_commit[ACTION] = ';'.join([ACTIVITY["A"]])
            for fieldname in data_commit:
                print(fieldname, data_commit[fieldname], sep=': ')
            print("-" * 40)
            log_wiki_to_csv(data_commit, csv_name)
            data_changes.append(data_commit)

    #Вывод репозиториев, с которыми возникли ошибки
    if error_repos:
        print("!=====Проблемные репозитории=====!")
        for rep in error_repos:
            print(rep)

    return data_changes
