from datetime import datetime, timedelta
from math import floor

from dateutil import parser as dateutil_parser
import pytz

from NikGapps.Git.Validate import Validate
from NikGapps.Git.GitApi import GitApi
from NikGapps.Git.PullRequest import PullRequest
import NikGapps.Git.GitConfig as Config

print("Checking if there is any existing workflow in progress")

try:
    workflows = GitApi.get_running_workflows(authenticate=False)
except Exception as e:
    print(str(e))
    try:
        workflows = GitApi.get_running_workflows(authenticate=True)
    except Exception as e:
        print(str(e))
        workflows = []

if len(workflows) > 0:
    print("Total Open Workflows: " + str(len(workflows)) + f", most recent being {workflows[0]['run_number']}")

if len(workflows) > 1:
    print(f"Open workflows detected, Let's wait for open workflows to finish")
    for workflow in workflows:
        print(workflow["run_number"])
    exit(0)

print("Finding the open pull requests")
try:
    requests = GitApi.get_open_pull_requests(authenticate=True)
except Exception as e:
    print(str(e))
    try:
        requests = GitApi.get_open_pull_requests(authenticate=True)
    except Exception as e:
        print(str(e))
        requests = []

print("Total Open Pull Requests: " + str(len(requests)))

for request in requests:
    print("-------------------------------------------------------------------------------------")
    pr_number = request["number"]
    pr = PullRequest(pr_number, request, authenticate=True)
    pr_url = request["url"]
    print("Validating pull request " + str(pr_url))
    failure_reason = Validate.pull_request(pr)
    print()
    if len(failure_reason) > 0:
        print("Checking if comments already made")
        comments = GitApi.get_comments_from_pull_request(pr_number, authenticate=True)
        comments_len = len(comments)
        print("Total comments already made: " + str(comments_len))
        if comments_len > 0:
            last_commenter = comments[comments_len - 1]["user"]["login"]
            comment_body = comments[comments_len - 1]["body"]
            if str(last_commenter).__eq__("nikgapps") or str(last_commenter).__eq__("nikhilmenghani"):
                updated_at = comments[comments_len - 1]["updated_at"]
                try:
                    d = dateutil_parser.parse(updated_at)
                    print("Comment already made on: " + str(d))
                    print()
                    print(comment_body)
                    print()
                    datetime_utc = datetime.now(pytz.timezone('UTC'))
                    date_diff = datetime_utc - d
                    seconds = date_diff.seconds + (date_diff.days * 86400)
                    hours = floor(seconds / 3600)
                    sec = timedelta(seconds=seconds)
                    d = datetime(1, 1, 1) + sec
                    print("Last comment was %d:%d:%d:%d ago" % (d.day - 1, d.hour, d.minute, d.second))
                    if hours >= Config.hours_before_close_pr:
                        message = None
                        if not str(comment_body).__contains__(f"Closing as no action was performed in last"):
                            message = f"Closing as no action was performed in last {Config.hours_before_close_pr} hours"
                        print("Closing the pull request")
                        if GitApi.close_pull_request(pull_number=pr_number, message=message):
                            print("Successfully Closed!")
                        else:
                            print("Failed to close the pull request")
                    else:
                        print("Moving on!")
                except Exception as e:
                    print(f"Exception occurred while parsing updated_at {updated_at} : " + str(e))
                continue
        GitApi.comment_on_pull_request(pr_number, failure_reason)
    else:
        print("Validation Successful!")
        print("Requesting a merge")
        if GitApi.merge_pull_request(pr_number):
            print("Successfully merged!")
        else:
            print("Failed to merge!")
    print()

print("end of program")
