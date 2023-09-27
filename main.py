import functions_framework
import json
import requests
from os import getenv

token = getenv("GITHUB_ACCESS_TOKEN")

# almost ~34 api calls 
@functions_framework.http
def fetch_github_data(request):
    try:
        request_json = request.get_json(silent=True)
        username = request_json["username"]
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

        user_response = requests.get(
            f"https://api.github.com/users/{username}", headers=headers
        )
        user_response.raise_for_status()
        user_data = user_response.json()

        repos_response = requests.get(user_data["repos_url"], headers=headers)
        repos_response.raise_for_status()
        repos_data = repos_response.json()

        commits_response = requests.get(
            f"https://api.github.com/search/commits?q=author:{username}&per_page=1",
            headers={**headers, "Accept": "application/vnd.github.cloak-preview"},
        )
        commits_response.raise_for_status()
        commits_data = commits_response.json()
        commits = commits_data["total_count"]

        stars_response = requests.get(
            f"https://api.github.com/users/{username}/starred", headers=headers
        )
        stars_response.raise_for_status()
        stars_data = stars_response.json()
        starred_repos = len(stars_data)

        events_response = requests.get(
            f"https://api.github.com/users/{username}/events", headers=headers
        )
        events_response.raise_for_status()
        events_data = events_response.json()
        event_types = [event["type"] for event in events_data]
        event_count = len(event_types)
        event_breakdown = {}

        for event_type in event_types:
            if event_type not in event_breakdown:
                event_breakdown[event_type] = 0
            event_breakdown[event_type] += 1

        for event_type, count in event_breakdown.items():
            event_breakdown[event_type] = round(count / event_count * 100, 2)

        repo_info = []
        for repo in repos_data:
            repo_name = repo["name"]
            repo_stars = repo["stargazers_count"]
            repo_forks = repo["forks_count"]
            repo_url = repo["html_url"]
            print(repo_url)
            languages_response = requests.get(
                f"https://api.github.com/repos/{username}/{repo_name}/languages",
                headers=headers,
            )
            languages_response.raise_for_status()
            languages_data = languages_response.json()

            repo_info.append(
                {
                    "name": repo_name,
                    "stars": repo_stars,
                    "forks": repo_forks,
                    "url": repo_url,
                    "languages": languages_data,
                }
            )

        user_info = {
            "username": username,
            "created_at": user_data.get("created_at"),
            "updated_at": user_data.get("updated_at"),
            "total_private_repos": user_data.get("total_private_repos"),
            "followers": user_data.get("followers"),
            "following": user_data.get("following"),
            "owned_private_repos": user_data.get("owned_private_repos"),
            "company": user_data.get("company"),
            "blog": user_data.get("blog"),
            "location": user_data.get("location"),
            "bio": user_data.get("bio"),
            "twitter_username": user_data.get("twitter_username"),
            "starred_repos": starred_repos,
            "event_breakdown": event_breakdown,
            "repositories": repo_info,
            "total_commits": commits,
        }

        return {"user_info": user_info}

    except requests.exceptions.HTTPError as _:
        return {"err": "500: Internal Server Error"}

    except Exception as _:
        return {"err": "500: Internal Server Error"}
