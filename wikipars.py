from git import Repo, Commit, Tree, Diff
import os
import time

def wikiparser(client, repositories, path_drepo, csv_name):
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
            data_commit["login"] = commit.author
            data_commit["datetime"] = time.asctime(time.localtime(commit.committed_date))
            if parent:
                data_commit["page"] = [diff.b_path for diff in parent[0].diff(commit)]
                data_commit["action"] = [activity[diff.change_type] for diff in parent[0].diff(commit)]
            else:
                #Первый коммит
                data_commit["page"] = [diff.b_path for diff in commit.diff(EMPTY_TREE_SHA)]
                data_commit["action"] = [activity["A"]]
            data_commit["revision id"] = commit
            data_commit["diff"] = commit.diff()
            for i in data_commit:
                print(i, data_commit[i], sep=': ')
            print("-------------------------------")
            data_changes.append(data_commit)

    #Вывод репозиториев, с которыми возникли ошибки
    if error_repos:
        print("!=====Проблемные репозитории=====!")
        for rep in error_repos:
            print(rep)

    return data_changes