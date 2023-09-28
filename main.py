import functions_framework
import requests
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
    print(GITHUB_ACCESS_TOKEN)
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
        # other stats
        "totalRepositories": res["repositories"]["totalCount"],
        "followers": res["followers"]["totalCount"],
        "following": res["following"]["totalCount"],
    }

    return usr


@functions_framework.http
def fetch_github_data(req: flask.Request):
    if req.method != "GET":  ## TODO: change it to POST
        return {
            "statusCode": 405,
            "error": "method not allowed",
        }, 405

    body = req.get_json(silent=True)
    username = req.args.get("username")  ## TODO: change it back to post
    # username = body["username"]

    resp = query_github_api(username)
    return resp, resp["statusCode"]


# Github Graphql Query used to obtained data
GRAPHQL_QUERY = """
query {
	rateLimit {
		cost
		limit
		nodeCount
		remaining
	}

	user(login: "Shivam010") {
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

		followers(first: 1) {
			totalCount
		}
		following(first: 1) {
			totalCount
		}

		repositories {
			totalCount
		}
	} # user end
}
"""
