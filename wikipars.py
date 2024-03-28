from git import Repo, Commit, Tree, Diff
import os
import time
import csv

WIKI_FIELDNAMES = ['repository name', 'author name', 'author login', 'datetime', 'page', 'action', 'revision id', 'diff']

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
        print("=================", name_rep, "=================")
        #Проверяем, есть ли репозиторий в папке
        dir_path = path_drepo + "/" + name_rep
        if os.path.exists(dir_path):
            #Обновляем репозиторий
            repo = Repo(dir_path)
            repo.remotes.origin.pull()
        else:
            #Клонируем репозиторий в папку
            dir_path = path_drepo + "/" + name_rep
            os.makedirs(dir_path, exist_ok=True)
            repo_url = f"git@github.com:{name_rep}.wiki.git"
            try:
                repo = Repo.clone_from(repo_url, dir_path)
            except Exception as e:
                print(e)
                error_repos.append(name_rep)
                continue

        #Вывод изменений
        EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
        wiki_commits = repo.iter_commits(all=True)
        activity = {"A" : "Страница добавлена", "M" : "Страница изменена", "D" : "Страница удалена", "R":"Страница переименована"}
        for commit in wiki_commits:
            data_commit = dict()
            parent = commit.parents
            data_commit["repository name"] = name_rep
            data_commit["author name"] = commit.author
            if commit.author.email:
                try:
                    data_commit["author login"] = commit.author.email.split('+')[1].split('@users')[0] 
                except:
                    pass
            data_commit["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S%z",time.gmtime(commit.committed_date))
            if parent:
                data_commit["page"] = ';'.join([diff.b_path for diff in parent[0].diff(commit)])
                data_commit["action"] =';'.join([activity[diff.change_type] for diff in parent[0].diff(commit)])
            else:
                #Первый коммит
                data_commit["page"] = ';'.join([diff.b_path for diff in commit.diff(EMPTY_TREE_SHA)])
                data_commit["action"] = ';'.join([activity["A"]])
            data_commit["revision id"] = commit
            data_commit["diff"] = commit.diff()
            for i in data_commit:
                print(i, data_commit[i], sep=': ')
            print("-------------------------------")
            log_wiki_to_csv(data_commit, csv_name)
            data_changes.append(data_commit)

    #Вывод репозиториев, с которыми возникли ошибки
    if error_repos:
        print("!=====Проблемные репозитории=====!")
        for rep in error_repos:
            print(rep)


    return data_changes
