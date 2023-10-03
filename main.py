from dotenv import load_dotenv

# load envs from .env file
load_dotenv()

from flask import Flask, request
import internal.utils as utils
from internal.fetch_stats import fetch_user_data
from internal.analyse_user import analyse_user
import os


# Flask app
app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return {"status_code": 404, "error": "404 - not found"}, 404


@app.errorhandler(405)
def method_not_allowed(e):
    return {
        "statusCode": 405,
        "error": "method not allowed",
    }, 405


@app.errorhandler(500)
def internal_error(e):
    print(e)
    app.logger.error("handler something went wrong", e)
    return {"status_code": 500, "error": "500 - something went wrong"}, 500


@app.route("/")
def home_route():
    return {
        "status_code": 200,
        "message": "Hello 👋, Welcome to GUA!",
        "url": "https://github.com/Shivam010/github-user-analysis",
    }, 200


@app.route("/fetch")
def fetch_github_user_data_route():
    try:
        if request.method != "GET":  ## TODO: change it to POST
            return {
                "statusCode": 405,
                "error": "method not allowed in fetch",
            }, 405

        # body = request.get_json(silent=True)
        # username = body["username"]
        username = request.args.get("username")  ## TODO: change it back to post
        nocache = False
        if request.args.get("nocache"):
            nocache = True

        # Check if the username is provided
        if not username:
            return {
                "statusCode": 400,
                "error": "Username not provided in the request body",
            }, 400

        resp = fetch_user_data(username, nocache)
        return resp, resp["statusCode"], {"Cache-Control": "public"}

    except Exception as err:
        print("exception something went wrong", err)
        return {
            "statusCode": 500,
            "error": "500: Internal Server Error",
        }, 500


@app.route("/check")
def check_volume():
    dir = utils.MOUNT_DIRECTORY
    res = os.listdir(dir)
    return {
        "list": res,
    }, 200


@app.route("/analyse/<username>")
def analyse_username(username: str):
    try:
        query = request.args.get("query")
        if query is None:
            query = "How is the code documented?"

        nocache = False
        if request.args.get("nocache"):
            nocache = True

        # analyze user
        resp = analyse_user(username, query, nocache)
        return resp, resp["statusCode"], {"Cache-Control": "public"}

    except Exception as err:
        print("exception something went wrong in analyze:", err)
        return {
            "statusCode": 500,
            "error": "500: Internal Server Error",
        }, 500
