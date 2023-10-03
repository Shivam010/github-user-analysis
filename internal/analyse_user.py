import internal.utils as utils
import internal.fetch_stats as gstats
import internal.fetch_files as gfiles
import json


def analyse_user(username: str, nocache=False):
    # fetch user's stats
    userStats = gstats.fetch_user_data(username, nocache)
    if userStats is None:
        return {
            "statusCode": 500,
            "error": f"500 - Something went wrong - username detail can not be found",
        }
    if "error" in userStats:
        return userStats

    userStats = userStats["data"]
    topRepos = userStats.get("topRepositories", [])
    jsrepo = gfiles.find_js_repo(topRepos)
    if jsrepo is None:
        return {
            "statusCode": 404,
            "error": "no js or ts repo found in topRepos",
            "userStats": userStats,
        }

    repoWithOwner = str(jsrepo.get("nameWithOwner", ""))
    files = gfiles.fetch_repo_files(
        repoWithOwner.split("/")[0],  # owner's username
        repoWithOwner.split("/")[1],  # repo name
        nocache,
    )

    return {
        "statusCode": 200,
        "analysisedRepo": repoWithOwner,
        "files": files,
        "userStats": userStats,
    }
