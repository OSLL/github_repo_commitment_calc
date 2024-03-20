from git import Repo, Commit, Tree, Diff
import shutil
import os
import time

def delete_everything_in_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)

def wikiparser(client, repositories, path_drepo, csv_name):
    path = path_drepo  #Путь к директории для репозитория
    #Создаем список репозиториев из файла
    with open(repositories, 'r') as file:
        list_repos = [x for x in file.read().split('\n') if x]
    error_repos = []

    for name_rep in list_repos:
        print("=================", name_rep, "=================")
        #Удаляем содержимое папки
        delete_everything_in_folder(path)
        #Клонируем репозиторий в папку
        try:
            repo_url = f"git@github.com:{name_rep}.wiki.git"
            repo = Repo.clone_from(repo_url, path)
        except Exception as e:
            print(e)
            error_repos.append(name_rep)
            continue

        #Вывод изменений
        EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
        wiki_commits = repo.iter_commits(all=True)
        activity = {"A" : "Страница добавлена", "M" : "Страница изменена", "D" : "Страница удалена", "R":"Страница переименована"}
        data_changes = []
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
    print("!=====Проблемные репозитории=====!")
    for rep in error_repos:
        print(rep)

    return data_changes