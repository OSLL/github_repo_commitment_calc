from git import Repo, Commit, Tree, Diff
import shutil
import os
import time
def delete_everything_in_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)

path = "/home/hom1e/KAFEDRAAAAA/local" #Путь к директории для репозитория

#удаляем содержимое папки
delete_everything_in_folder(path)

#Клонируем репозиторий в папку
repo_url = "https://github.com/OSLL/github_repo_commitment_calc.wiki.git"
repo = Repo.clone_from(repo_url, path)

prev_commits = list(repo.iter_commits(all=True, max_count=10))  # last 10 commits from all branches

next_commit_ind = 1
for commit in prev_commits[:-1]:
    #print(commit.author, time.asctime(time.localtime(commit.committed_date)), "here page", commit, commit.diff(prev_commits[next_commit_ind]), sep=" --- ")
    print("login:", commit.author)
    print("datetime:", time.asctime(time.localtime(commit.committed_date)))
    print("page:", "Here page")
    print("revision id:", commit)
    print("action:", *[diff.change_type for diff in prev_commits[next_commit_ind].diff(commit)])
    print("diff:", commit.diff())
    print("-------------------------------")
    """for diff in commit.diff(prev_commits[next_commit_ind]):
        print(diff)
        print(diff.change_type)"""
    next_commit_ind += 1



#help(commit.diff())
#help(Diff)

