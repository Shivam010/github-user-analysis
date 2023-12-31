import internal.utils as utils
import internal.fetch_stats as gstats
import internal.fetch_files as gfiles
from internal.parse_js_file_content import parse_js_file_content, convert_to_plain_text
import internal.openapi as openapi


def analyse_user(username: str, query: str, nocache=False):
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
    repoOwner = repoWithOwner.split("/")[0]
    repoName = repoWithOwner.split("/")[1]
    files = gfiles.fetch_repo_files(
        repoOwner,  # owner's username
        repoName,  # repo name
        nocache,
    )
    if "error" in files:
        return files  # error

    if len(files) == 0:
        return {
            "statusCode": 412,
            "analysisedRepo": repoWithOwner,
            "message": "no files found in it",
            "userStats": userStats,
        }

    # now, convert all files into corresponding segments and create a plain text representation out of it
    plainTextRepoDetails, parsedFiles = process_repo_files_to_plain_text(
        repoOwner,
        repoName,
        files,
        nocache,
    )

    prompt = (
        f"For Repo - {repoWithOwner}, these are the extracted details of the files in the repo: \n"
        + plainTextRepoDetails
        + "\n\n Now, use the provided context of the repo, answer to the point the following question with reference to the repo: "
        + query
        + "\n\n Always, just return a brief summary on the answer. Plus, if you are not able to pin point anything just say so."
    )
    prompt2 = (
        openapi.systemPrompt + "\n" + plainTextRepoDetails + "\n" + "Question: " + query
    )

    resp = {
        "statusCode": 200,
        "analysisedRepo": repoWithOwner,
        "inputQuery": query,
        "zparsedFiles": parsedFiles,
        "prompt": prompt,
        "prompt2": prompt2,
        "userStats": userStats,
    }
    try:
        resp["gpt3.5prediction"] = openapi.generate_response(
            plainTextRepoDetails,
            query,
        )
    except:
        resp["gpt3.5prediction"] = {
            "message": "error: openapi call paniced",
            "usage": {},
        }

    return resp


def process_repo_files_to_plain_text(
    repoOwner: str, repoName: str, files: list, nocache=False
):
    # now, convert each file into corresponding segments
    parsedFiles = []

    def parse_and_store_fnc(file, content: str):
        # print(file["name"], "started")
        parsedFiles.append(
            {
                "name": file["name"],
                "path": file["path"],
                "info": parse_js_file_content(file["name"], content),
            }
        )
        # print(file["name"], "ended")

    # iterate over all files
    for file in files:
        iterate_files(
            repoOwner,
            repoName,
            file,
            parsedFiles,
            parse_and_store_fnc,
            nocache,
        )
    plainTextRepoDetails = convert_to_plain_text(parsedFiles)
    return plainTextRepoDetails, parsedFiles


# iterate_files nestedly in all
def iterate_files(
    owner: str,
    repo: str,
    cur_file,
    parsedFiles,
    parse_and_store_fnc,
    nocache=False,
):
    if cur_file is None:
        return

    if len(parsedFiles) >= 100:
        return

    if "files" in cur_file:
        # it's directory then
        for file in cur_file["files"]:
            iterate_files(owner, repo, file, parsedFiles, parse_and_store_fnc, nocache)
        return

    content = utils.download_github_file(
        owner,
        repo,
        path=cur_file["path"],
        nocache=nocache,
    )
    if content is not None:
        parse_and_store_fnc(cur_file, content)
