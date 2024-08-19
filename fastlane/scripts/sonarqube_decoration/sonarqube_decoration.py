import argparse
import fileinput
import logging
import os

import requests

logging.basicConfig(level=logging.INFO)


def write_measure_in_sonarqube_decoration_template(measure_name, measure):
    """
    Write the measure in the sonarqube decoration template file.
    :param measure_name: The measure name to replace in the template file.
    :param measure: The measure that replace the measure_name in the template file.
    """
    with fileinput.FileInput(
            "{}/sonarqube_decoration_template.md".format(os.path.dirname(__file__)),
            inplace=True,
            backup=".bak",
    ) as file:
        for line in file:
            line = line.replace("#{}#".format(measure_name), measure)
            print(line, end="")


class SonarqubeDecoration:
    def __init__(self, sonar_project_name) -> None:
        self._project_id = os.environ.get("CI_MERGE_REQUEST_PROJECT_ID")
        self._merge_request_iid = os.environ.get("CI_MERGE_REQUEST_IID")
        self._branch = os.environ.get("CI_COMMIT_REF_NAME")
        self._sonar_project_name = sonar_project_name
        self._gitlab_api_token = os.environ.get("KS739_API_TOKEN")

    def get_measure(self, measure_name):
        """
        Get the sonarqube measure based on a measure name.
        :param measure_name: The measure name to get.
        """
        url = "http://sonarqube-prd.intra.arkea.com:8080/api/measures/component?component={}&branch={}&metricKeys={}".format(
            self._sonar_project_name, self._branch, measure_name
        )
        return requests.get(url).json()["component"]["measures"][0]["value"]

    def process_measure(self, measure_name):
        """
        Get a measure and add it in the template file.
        :param measure_name: The sonarqube measure to get.
        """
        measure = self.get_measure(measure_name)
        write_measure_in_sonarqube_decoration_template(measure_name, measure)

    def process_sonarqube_decoration(self):
        """
        Get all measures and add them in the template file.
        """
        write_measure_in_sonarqube_decoration_template(
            "project", self._sonar_project_name
        )
        write_measure_in_sonarqube_decoration_template("branch", self._branch)
        write_measure_in_sonarqube_decoration_template(
            "project_name", self._sonar_project_name
        )
        self.process_measure("alert_status")
        self.process_measure("violations")
        self.process_measure("bugs")
        self.process_measure("vulnerabilities")
        self.process_measure("security_hotspots")
        self.process_measure("code_smells")
        self.process_measure("coverage")
        self.process_measure("duplicated_lines_density")

    @staticmethod
    def prepare_data():
        """
        Transform the template file in string data in format for HTTP request.
        """
        file = open(
            "{}/sonarqube_decoration_template.md".format(os.path.dirname(__file__)), "r"
        )
        content = file.read()
        if not file.closed:
            file.close()
        return {"body": content}

    def add_note_in_merge_request(self):
        """
        Process the sonarqube template file and post a note in a Gitlab CI/CD merge request.
        """
        url = "https://gitlark.s.arkea.com/api/v4/projects/{}/merge_requests/{}/notes".format(
            self._project_id, self._merge_request_iid
        )
        headers = {"PRIVATE-TOKEN": self._gitlab_api_token}
        self.process_sonarqube_decoration()
        sonarqube_decoration_data = self.prepare_data()
        requests.post(url, headers=headers, params=sonarqube_decoration_data)

    def add_thread_in_merge_request(self):
        """
        Process the sonarqube template file and post a note in a Gitlab CI/CD merge request.
        """
        url = "https://gitlark.s.arkea.com/api/v4/projects/{}/merge_requests/{}/discussions".format(
            self._project_id, self._merge_request_iid
        )
        headers = {"PRIVATE-TOKEN": self._gitlab_api_token}
        self.process_sonarqube_decoration()
        sonarqube_decoration_data = self.prepare_data()
        requests.post(url, headers=headers, params=sonarqube_decoration_data)

    def add_sonarqube_decoration_in_merge_request(self):
        """
        Add a sonarqube decoration in a specified merge request. The decoration can be a note if the sonarqube analysis is OK or a thread if it is KO.
        """
        alert_status = self.get_measure("alert_status")
        if alert_status == "OK":
            self.add_note_in_merge_request()
        else:
            self.add_thread_in_merge_request()


def main():
    parser = argparse.ArgumentParser(
        description="Instana manager for crashes management of apps"
    )
    parser.add_argument(
        "-a",
        "--add",
        type=str,
        nargs=1,
        metavar="sonar_project_name",
        default=None,
        help="Add sonarqube decoration in merge request.",
    )
    args = parser.parse_args()
    if args.add:
        sonarqube_decoration = SonarqubeDecoration(args.add[0])
        sonarqube_decoration.add_sonarqube_decoration_in_merge_request()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
