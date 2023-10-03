import requests
import datetime
from os import getenv
import json

# MOUNT_DIRECTORY
MOUNT_DIRECTORY = getenv("MOUNT_DIRECTORY")

# GitHub GraphQL API endpoint
GITHUB_GRAPHQL_API_ENDPOINT = "https://api.github.com/graphql"

# GitHub personal access token for authentication
GITHUB_ACCESS_TOKEN = getenv("GITHUB_ACCESS_TOKEN")


# Handles rate limiting
def handle_rate_limiting(response: requests.Response):
    reset_time = int(response.headers["X-RateLimit-Reset"])
    reset_time = datetime.utcfromtimestamp(reset_time)
    reset_time = reset_time.strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "statusCode": 429,
        "error": f"Too many requests. Rate limit exceeded. Try again after {reset_time}",
    }


# Make api request
def fetch_github_query(query: str, variables: dict):
    headers = {
        "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        GITHUB_GRAPHQL_API_ENDPOINT,
        headers=headers,
        json={"query": query, "variables": variables},
    )

    # rate limit reached, github returns 403 for rate limiting
    if resp.status_code == 403:
        return handle_rate_limiting(resp)

    if resp.status_code != 200:
        return {
            "statusCode": resp.status_code,
            "error": f"{resp.status_code} - Something went wrong",
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
        print("something went wrong", body["errors"])

        return {
            "statusCode": 500,
            "error": "500 - Something went wrong",
        }

    return body


def readData(fname: str):
    try:
        f = open(MOUNT_DIRECTORY + "/" + fname, "r")
        data = f.read()
        data = json.loads(data)
        return data
    except:
        return None


def writeData(fname: str, txt: str):
    f = open(MOUNT_DIRECTORY + "/" + fname, "w")
    f.write(txt)
    f.close()


def appendData(fname: str, txt: str):
    f = open(MOUNT_DIRECTORY + "/" + fname, "a")
    f.write(txt)
    f.close()
