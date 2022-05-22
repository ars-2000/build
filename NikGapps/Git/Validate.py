import os
from NikGapps.Git.PullRequest import PullRequest
import re


class Validate:

    @staticmethod
    def pull_request(pr: PullRequest):
        failure_reason = []
        files_changed = pr.get_files_changed(True)
        total = len(files_changed)
        regex = '[^a-zA-Z0-9_-]'
        print("Total files changed: " + str(total))
        for i in range(0, total):
            print("-------------------------------------------------------------------------------------")
            file_name = str(files_changed[i]["filename"])
            raw_file_name = os.path.splitext((os.path.basename(file_name)))[0]
            print("Validating: " + file_name)
            print("-------------------------------------------------------------------------------------")
            print("- checking file name: " + raw_file_name)
            if file_name.__contains__("#") or file_name.__contains__("!"):
                failure_reason.append(f"{file_name} contains symbols in the name which are not allowed. "
                                      f"Only alphanumeric names are allowed!")
            if not file_name.endswith(".config"):
                failure_reason.append(f"{file_name} doesn't have .config extension, we only accept config files!")
            print("- checking if android version is present")
            if not (file_name.startswith("10" + os.path.sep) or file_name.startswith("11" + os.path.sep)
                    or file_name.startswith("12" + os.path.sep) or file_name.startswith("12.1" + os.path.sep)):
                if file_name.startswith("archive" + os.path.sep):
                    failure_reason.append(f"You cannot modify archived file {file_name}")
                else:
                    failure_reason.append(f"{file_name} must be part of Android Version folder, not outside of it!")
            print("- checking if filename is alphanumeric")
            regex_match = re.search(regex, raw_file_name)
            if regex_match is not None:
                failure_reason.append(
                    f"{file_name} is not an aphanumeric name, "
                    f"make sure the name of config file is between A-Z and 0-9 "
                    f"additionally, accepted symbols are - (dash) or _ (underscore) "
                    f"any symbols including but not limited to (, ' . # ! *) are not accepted in the name")
                print(regex_match)
            print("- checking file status")
            file_status = str(files_changed[i]["status"])
            if not file_status.__eq__("added"):
                failure_reason.append(
                    f"Cannot merge the changes automatically since {file_name} is either modified or removed, "
                    "Wait for someone to manually review!")
        return failure_reason
