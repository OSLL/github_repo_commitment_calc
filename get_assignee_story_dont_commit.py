def get_assignee_story(github_object):
    repo_owner = "OSLL"
    repo_name = "github_repo_commitment_calc"
    access_token = "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"

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{github_object.number}" if type(
        github_object) is PullRequest.PullRequest else\
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{github_object.number}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Получение данных: {response.reason, response.status_code, response.url}")
        event = response.json()
        print(event)
        creator_name = event["assignee"]["login"]
        print(f"Создатель последнего события: {creator_name}")
    else:
        print(f"Ошибка при получении данных: {response.reason, response.status_code, response.url}")

    assignee_result = ""
    events = github_object.get_issue_events() if type(
        github_object) is PullRequest.PullRequest else github_object.get_events()
    for event in events:
        if event.event == "assigned" or event.event == "unassigned":
            date = event.created_at
            if event.event == "assigned":
                assigner = event.actor.login
                assignee = event.assignee.login
                assignee_result += f"{date}: {assigner} -> {assignee}; "
            else:
                assigner = "placeholder"  # event.actor не работает (баг pygithub)
                assignee = event.assignee.login
                assignee_result += f"{date}: {assigner} -/> {assignee}; "
    return assignee_result