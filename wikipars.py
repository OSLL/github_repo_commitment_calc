from git import Repo, Commit, Tree, Diff
import shutil
import os
import time
def delete_everything_in_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)

path = "/home/hom1e/KAFEDRAAAAA/local"  #Путь к директории для репозитория

#Создаем список репозиториев из файла
with open("repolist", 'r') as file:
    list_repos = [x for x in file.read().split('\n') if x]

for name_rep in list_repos:
    print("=================", name_rep, "=================")
    #Удаляем содержимое папки
    delete_everything_in_folder(path)
    #Клонируем репозиторий в папку
    repo_url = f"https://github.com/{name_rep}.wiki.git"
    repo = Repo.clone_from(repo_url, path)

    prev_commits = list(repo.iter_commits(all=True))

    activity = {"A" : "Страница добавлена", "M" : "Страница изменена", "D" : "Страница удалена", "R":"Страница переименована"}
    for ind in range(len(prev_commits[:-1])):
        commit = prev_commits[ind]
        print("login:", commit.author)
        print("datetime:", time.asctime(time.localtime(commit.committed_date)))
        print("page:", *[diff.b_path for diff in prev_commits[ind + 1].diff(commit)])
        print("revision id:", commit)
        print("action:", *[activity[diff.change_type] for diff in prev_commits[ind + 1].diff(commit)])
        print("diff:", commit.diff())
        print("-------------------------------")
