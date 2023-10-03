import internal.utils as utils
import internal.fetch_stats as gstats
import json


# find js repo
def find_js_repo(repos):
    if repos is None:
        return None

    for repo in repos:
        if repo["nameWithOwner"].endswith("-fork"):
            continue
        # check primary lang
        if repo["primaryLanguage"] is not None:
            name = repo["primaryLanguage"]["name"]
            if name == "JavaScript" or name == "TypeScript":
                return repo

        # check other lang
        if repo["langauges"] is not None:
            for lang in repo["langauges"]:
                if lang is None:
                    continue
                name = lang["name"]
                if name == "JavaScript" or name == "TypeScript":
                    return repo
    return None


# Function to fetch files
def fetch_repo_files(owner: str, repo: str, nocache=False):
    ckey = "-" + owner + "-" + repo
    cval = utils.readData(ckey, nocache)
    if cval is not None:
        return cval

    resp = utils.fetch_github_query(
        FILES_GRAPHQL_QUERY,
        {
            "owner": owner.strip(),
            "repo": repo.strip(),
        },
    )
    if "error" in resp:
        return resp

    list = []
    repo = resp["data"]["repository"]
    if repo is not None:
        tree = repo["object"]
        list = parse_tree(tree)

    utils.writeData(ckey, json.dumps(list))
    return list


# parse repo tree to file list
def parse_tree(tree, prefix="/"):
    if tree is None:
        return []

    entries = tree.get("entries", [])
    parsed_entries = []

    for entry in entries:
        if entry is None:
            continue

        name = str(entry.get("name", ""))
        ftype = entry["type"]

        # remove non js files
        if ftype == "blob" and not (
            name.endswith(".js")
            or name.endswith(".ts")
            or name.endswith(".tsx")
            or name.endswith(".jsx")
            # or name.endswith(".json")
        ):
            continue

        node = {
            "name": name,
            "path": prefix + name,
        }

        if ftype == "tree":
            node["files"] = parse_tree(entry["object"], prefix + name + "/")

        parsed_entries.append(node)

    return parsed_entries


FILES_GRAPHQL_QUERY = """
query ($owner: String!, $repo: String!) {
	rateLimit {
		cost
		limit
		nodeCount
		remaining
		resetAt
		used
	}

	repository(owner: $owner, name: $repo) {
		object(expression: "HEAD:") {
			... on Tree {
				entries {
					name
					type
					object {
						... on Blob {
							byteSize
						}
						... on Tree {
							entries {
								name
								type
								object {
									__typename
									... on Blob {
										byteSize
									}
									... on Tree {
										entries {
											name
											type
											object {
												... on Blob {
													byteSize
												}

												... on Tree {
													entries {
														name
														type
														object {
															... on Blob {
																byteSize
															}
														}
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}
"""
