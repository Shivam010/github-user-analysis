import functions_framework
import logging
import requests
from datetime import datetime
import flask
from dotenv import load_dotenv
from os import getenv

# load envs from .env file
load_dotenv()

# GitHub GraphQL API endpoint
GITHUB_GRAPHQL_API_ENDPOINT = "https://api.github.com/graphql"

# GitHub personal access token for authentication
GITHUB_ACCESS_TOKEN = getenv("GITHUB_ACCESS_TOKEN")


# Function to query GitHub GraphQL API
def query_github_api(username: str):
    headers = {
        "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        GITHUB_GRAPHQL_API_ENDPOINT,
        headers=headers,
        json={
            "query": GRAPHQL_QUERY,
            "variables": {
                "username": username.strip(),
            },
        },
    )

    # rate limit reached, github returns 403 for rate limiting
    if resp.status_code == 403:
        return handle_rate_limiting(resp)

    if resp.status_code != 200:
        return {
            "statusCode": 500,
            "error": "500 - Something went wrong",
        }

    try:
        body = resp.json()
    except:
        return {
            "statusCode": 500,
            "error": "500 - Something went wrong",
        }

    # handle errors in body
    if "errors" in body:
        # check for gql rate limiting
        for error in body["errors"]:
            if error.type == "RATE_LIMITED":
                return handle_rate_limiting(resp)

        # for all other errors log the error
        logging.error("something went wrong", body["errors"])

        return {
            "statusCode": 500,
            "error": "500 - Something went wrong",
        }

    usr = body["data"]["user"]
    usr = format_user_response(usr)
    return {
        "data": usr,
        "statusCode": 200,
    }


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

    # total stars received for repositories
    usr["totalStarredRepositories"] = res["starredRepositories"]["totalCount"]

    # total stars received for repositories
    usr["totalStarsReceived"] = sum(
        repo["stargazerCount"] for repo in res["repositories"]["nodes"]
    )

    # top repositories user has contributed to in any way
    top_repos = []
    for repo in res["topRepositories"]["nodes"]:
        top_repos.append(format_repos_response(repo))
    usr["topRepositories"] = top_repos

    # recently contributed repos
    recent_repos = []
    for repo in res["recentlyContributedTo"]["nodes"]:
        recent_repos.append(format_repos_response(repo))
    usr["recentlyContributedRepositories"] = recent_repos

    return usr


# Formats the github api's repos response
def format_repos_response(res):
    repo = {
        "url": res["url"],
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


# Handles rate limiting
def handle_rate_limiting(response: requests.Response):
    reset_time = int(response.headers["X-RateLimit-Reset"])
    reset_time = datetime.utcfromtimestamp(reset_time)
    reset_time = reset_time.strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "statusCode": 429,
        "error": f"Too many requests. Rate limit exceeded. Try again after {reset_time}",
    }


@functions_framework.http
def fetch_github_data(req: flask.Request):
    try:
        if req.method != "GET":  ## TODO: change it to POST
            return {
                "statusCode": 405,
                "error": "method not allowed",
            }, 405

        body = req.get_json(silent=True)
        username = req.args.get("username")  ## TODO: change it back to post
        # username = body["username"]

        # Check if the username is provided
        if not username:
            return {
                "statusCode": 400,
                "error": "Username not provided in the request body",
            }, 400

        resp = query_github_api(username)
        return resp, resp["statusCode"]

    except Exception as err:
        logging.error("something went wrong", err)
        return {
            "statusCode": 500,
            "error": "500: Internal Server Error",
        }, 500


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
	url
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
