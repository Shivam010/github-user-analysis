import internal.utils as utils
import json


# Function to fetch user data
def fetch_user_data(username: str, nocache=False):
    ckey = username
    cval = utils.readData(ckey, nocache)
    if cval is not None:
        return cval

    resp = utils.fetch_github_query(
        GRAPHQL_QUERY,
        {
            "username": username.strip(),
        },
    )
    if "error" in resp:
        return resp

    usr = resp["data"]["user"]
    usr = format_user_response(usr)
    data = {
        "data": usr,
        "statusCode": 200,
    }

    utils.writeData(ckey, json.dumps(data))
    return data


# Formats the github api response, based on the graphql query
def format_user_response(res):
    usr = {
        "bio": res["bio"],
        "name": res["name"],
        "username": res["username"],
        "createdAt": res["createdAt"],
        "updatedAt": res["updatedAt"],
        "location": res["location"],
        "twitterUsername": res["twitterUsername"],
        "socialAccounts": res["socialAccounts"]["nodes"],
        "isDeveloperProgramMember": res["isDeveloperProgramMember"],
        # other stats
        "totalRepositories": res["repositories"]["totalCount"],
        "followers": res["followers"]["totalCount"],
        "following": res["following"]["totalCount"],
        # related to sponsering
        "hasSponsorsListing": res["hasSponsorsListing"],
        "totalSponsors": res["sponsors"]["totalCount"],
        "totalSponsorshipAmountAsSponsorInCents": res[
            "totalSponsorshipAmountAsSponsorInCents"
        ],
        "totalSponsorings": res["sponsoring"]["totalCount"],
    }

    # contributions stats in past 1 years
    usr["oneYearContributionsStats"] = res["oneYearContributionsStats"]
    usr["oneYearContributionsStats"]["timePeriod"] = {
        "startedAt": res["oneYearContributionsStats"]["startedAt"],
        "endedAt": res["oneYearContributionsStats"]["endedAt"],
    }
    del usr["oneYearContributionsStats"]["startedAt"]
    del usr["oneYearContributionsStats"]["endedAt"]

    # total stars received for repositories
    usr["totalStarredRepositories"] = res["starredRepositories"]["totalCount"]

    # total stars received for repositories
    usr["totalStarsReceived"] = sum(
        repo["stargazerCount"] for repo in res["repositories"]["nodes"]
    )

    # top repositories user has contributed to in any way
    top_repos = []
    for repo in res["topRepositories"]["nodes"]:
        if repo is None:
            continue
        top_repos.append(format_repos_response(repo))
    usr["topRepositories"] = top_repos

    # recently contributed repos
    recent_repos = []
    for repo in res["recentlyContributedTo"]["nodes"]:
        if repo is None:
            continue
        recent_repos.append(format_repos_response(repo))
    usr["recentlyContributedRepositories"] = recent_repos

    return usr


# Formats the github api's repos response
def format_repos_response(res):
    repo = {
        "nameWithOwner": res["nameWithOwner"],
        "stargazerCount": res["stargazerCount"],
        "forkCount": res["forkCount"],
        "primaryLanguage": None,
        "langauges": [],
    }

    prime_lang = ""
    if res["primaryLanguage"] is not None and "name" in res["primaryLanguage"]:
        prime_lang = res["primaryLanguage"]["name"]

    all_langs = []
    for lang in res["languages"]["edges"]:
        lng = {
            "size": lang["size"],
            "name": lang["node"]["name"],
        }
        if lng["name"] == prime_lang:
            repo["primaryLanguage"] = lng
        all_langs.append(lng)

    repo["langauges"] = all_langs

    return repo


# Github Graphql Query used to obtained data
GRAPHQL_QUERY = """
query ($username: String!) {
	rateLimit {
		cost
		limit
		nodeCount
		remaining
		resetAt
		used
	}

	user(login: $username) {
		name
		twitterUsername
		username: login
		createdAt
		updatedAt
		location

		bio
		socialAccounts(first: 5) {
			nodes {
				displayName
				provider
				url
			}
			totalCount
		}

		isDeveloperProgramMember

		# contributions stats in past 1 years
		oneYearContributionsStats: contributionsCollection {
			startedAt
			endedAt

			restrictedContributionsCount

			totalIssueContributions
			totalCommitContributions
			totalPullRequestContributions
			totalPullRequestReviewContributions

			totalRepositoryContributions
			totalRepositoriesWithContributedIssues
			totalRepositoriesWithContributedCommits
			totalRepositoriesWithContributedPullRequests
			totalRepositoriesWithContributedPullRequestReviews

			popularIssueContribution {
				isRestricted
				issue {
					title
					# bodyText
					createdAt
					closedAt
					url
				}
			}

			popularPullRequestContribution {
				isRestricted
				pullRequest {
					url
					title
					# bodyText
					createdAt
					changedFiles
					reviewDecision
				}
			}

			hasAnyContributions
		}

		# top repositories user has contributed to in any way
		topRepositories(
			first: 50
			orderBy: { direction: DESC, field: STARGAZERS }
		) {
			nodes {
				...RepoDetails
			}
		}

		followers {
			totalCount
		}
		following {
			totalCount
		}

		# number of repositories the user has starred
		starredRepositories {
			totalCount
		}

		# recently contributed repos
		recentlyContributedTo: repositoriesContributedTo(first: 10) {
			nodes {
				...RepoDetails
			}
		}

		# for stars calculations only considering top 100
		repositories(
			first: 100
			ownerAffiliations: [OWNER, ORGANIZATION_MEMBER, COLLABORATOR]
			orderBy: { direction: DESC, field: STARGAZERS }
		) {
			totalCount
			nodes {
				url
				stargazerCount
			}
		}

		hasSponsorsListing
		totalSponsorshipAmountAsSponsorInCents
		sponsors {
			totalCount
		}
		sponsoring {
			totalCount
		}
	} # user end
}

fragment RepoDetails on Repository {
	nameWithOwner
	stargazerCount
	forkCount
	primaryLanguage {
		name
	}
	languages(first: 5) {
		edges {
			size
			node {
				name
			}
		}
	}
}
"""
