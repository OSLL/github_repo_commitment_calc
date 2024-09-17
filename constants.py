# For all
EMPTY_FIELD = 'Empty field'
TIMEDELTA = 0.05
TIMEZONE = 'Europe/Moscow'

# Fieldnames
REPO_NAME = 'repository name'
AUTHOR_NAME = 'author name'
AUTHOR_LOGIN = 'author login'
AUTHOR_EMAIL = 'author email'
DATE_AND_TIME = 'date and time'
CHANGED_FILES = 'changed files'
COMMIT_ID = 'commit id'
BRANCH = 'branch'
ADDED_LINES = 'added lines'
DELETED_LINES = 'deleted lines'
TITLE = 'title'
ID = 'id'
STATE = 'state'
COMMIT_INTO = 'commit into'
COMMIT_FROM = 'commit from'
CREATED_AT = 'created at'
CREATOR_NAME = 'creator name'
CREATOR_LOGIN = 'creator login'
CREATOR_EMAIL = 'creator email'
COMMENT_BODY = 'comment body'
COMMENT_CREATED_AT = 'comment created at'
COMMENT_AUTHOR_NAME = 'comment author name'
COMMENT_AUTHOR_LOGIN = 'comment author login'
COMMENT_AUTHOR_EMAIL = 'comment author email'
MERGER_NAME = 'merger name'
MERGER_LOGIN = 'merger login'
MERGER_EMAIL = 'merger email'
SOURCE_BRANCH = 'source branch'
TARGET_BRANCH = 'target branch'
ASSIGNEE_STORY = 'assignee story'
RELATED_ISSUES = 'related issues'
LABELS = 'labels'
MILESTONE = 'milestone'
NUMBER = 'number'
TASK = 'task'
CLOSER_NAME = 'closer name'
CLOSER_LOGIN = 'closer login'
CLOSER_EMAIL = 'closer email'
CLOSED_AT = 'closed at'
CONNECTED_PULL_REQUESTS = 'connected pull requests'
INVITED_LOGIN = 'invited login'
INVITE_CREATION_DATE = 'invite creation date'
INVITATION_URL = 'invitation url'
PAGE = 'page'
ACTION = 'action'
REVISION_ID = 'revision id'

# For commits
FORKED_REPO = False
ORIG_REPO_COMMITS = []
COMMIT_FIELDNAMES = (REPO_NAME, AUTHOR_NAME, AUTHOR_LOGIN, AUTHOR_EMAIL, DATE_AND_TIME, CHANGED_FILES, COMMIT_ID, BRANCH, ADDED_LINES, DELETED_LINES)

# For pull requests
PULL_REQUEST_FIELDNAMES = (REPO_NAME, TITLE, ID, STATE, COMMIT_INTO, COMMIT_FROM, CREATED_AT, CREATOR_NAME, CREATOR_LOGIN, CREATOR_EMAIL,
                           CHANGED_FILES, COMMENT_BODY, COMMENT_CREATED_AT, COMMENT_AUTHOR_NAME, COMMENT_AUTHOR_LOGIN, COMMENT_AUTHOR_EMAIL,
                           MERGER_NAME, MERGER_LOGIN, MERGER_EMAIL, SOURCE_BRANCH, TARGET_BRANCH, ASSIGNEE_STORY, RELATED_ISSUES, LABELS, MILESTONE)

# For issues
ISSUE_FIELDNAMES = (REPO_NAME, NUMBER, TITLE, STATE, TASK, CREATED_AT, CREATOR_NAME, CREATOR_LOGIN,
                    CREATOR_EMAIL, CLOSER_NAME, CLOSER_LOGIN, CLOSER_EMAIL, CLOSED_AT, COMMENT_BODY,
                    COMMENT_CREATED_AT, COMMENT_AUTHOR_NAME, COMMENT_AUTHOR_LOGIN, COMMENT_AUTHOR_EMAIL,
                    ASSIGNEE_STORY, CONNECTED_PULL_REQUESTS, LABELS, MILESTONE)

# For invites
INVITE_FIELDNAMES = (REPO_NAME, INVITED_LOGIN, INVITE_CREATION_DATE, INVITATION_URL)

# For wikis
EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # Хэш пустого дерева для сравнения с первым коммитом. Способ был найден здесь: https://stackoverflow.com/questions/33916648/get-the-diff-details-of-first-commit-in-gitpython
ACTIVITY = {"A": "Страница добавлена", "M": "Страница изменена", "D": "Страница удалена", "R": "Страница переименована"}
ENG_ACTIVITY = {"A": "Page added", "M": "Page modified", "D": "Page deleted", "R": "Page renamed"}
WIKI_FIELDNAMES = (REPO_NAME, AUTHOR_NAME, AUTHOR_LOGIN, DATE_AND_TIME, PAGE, ACTION, REVISION_ID, ADDED_LINES, DELETED_LINES)
