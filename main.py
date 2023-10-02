from dotenv import load_dotenv

# load envs from .env file
load_dotenv()

from flask import Flask, request
from github.fetch_stats import fetch_user_data


# Flask app
app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return {"status_code": 404, "error": "404 - not found"}, 404


@app.errorhandler(500)
def internal_error(e):
    print(e)
    app.logger.error("handler something went wrong", e)
    return {"status_code": 500, "error": "500 - something went wrong"}, 500


@app.route("/fetch")
def fetch_github_user_data_route():
    try:
        if request.method != "GET":  ## TODO: change it to POST
            return {
                "statusCode": 405,
                "error": "method not allowed",
            }, 405

        # body = request.get_json(silent=True)
        # username = body["username"]
        username = request.args.get("username")  ## TODO: change it back to post

        # Check if the username is provided
        if not username:
            return {
                "statusCode": 400,
                "error": "Username not provided in the request body",
            }, 400

        resp = fetch_user_data(username)
        return resp, resp["statusCode"], {"Cache-Control": "public"}

    except Exception as err:
        print("exception something went wrong", err)
        return {
            "statusCode": 500,
            "error": "500: Internal Server Error",
        }, 500
