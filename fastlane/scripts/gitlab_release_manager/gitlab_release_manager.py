import requests
import argparse
import os
import logging


class GitlabReleaseManager:
    def __init__(self, project_id, tag_name, app_name, app_version) -> None:
        self._base_url = f"https://gitlark.s.arkea.com/api/v4"
        self._project_id = project_id
        self._tag_name = tag_name
        self._app_name = app_name
        self._app_version = app_version
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)

    def _search_for_release(self):
        headers = {
            "JOB-TOKEN": os.environ.get("CI_JOB_TOKEN"),
        }
        return requests.get(
            f"{self._base_url}/projects/{self._project_id}/releases/{self._tag_name}",
            headers=headers,
        )

    def _create_release(self):
        new_release_data = {
            "name": f"Release {self._tag_name}",
            "tag_name": self._tag_name,
            "description": f"- {self._app_name}: {self._app_version}",
        }
        headers = {
            "Content-Type": "application/json",
            "JOB-TOKEN": os.environ.get("CI_JOB_TOKEN"),
        }
        return requests.post(
            f"{self._base_url}/projects/{self._project_id}/releases",
            headers=headers,
            json=new_release_data,
        )

    def _update_release(self, release):
        current_release_data = release.json()
        if self._app_name in current_release_data["description"]:
            fake_response = requests.models.Response()
            fake_response.status_code = 500
            fake_response.reason = f"{self._app_name} is already present in the release for tag {self._tag_name}"
            fake_response.url = f"{self._base_url}/projects/{self._project_id}/releases/{self._tag_name}"
            return fake_response
        else:
            new_release_data = current_release_data
            new_release_data["description"] = (
                new_release_data["description"]
                + f"\n- {self._app_name}: {self._app_version}"
            )
            headers = {
                "JOB-TOKEN": os.environ.get("CI_JOB_TOKEN"),
            }
            return requests.put(
                f"{self._base_url}/projects/{self._project_id}/releases/{self._tag_name}",
                json=new_release_data,
                headers=headers,
            )

    def process_release(self):
        release = self._search_for_release()
        if release.ok:
            response = self._update_release(release)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as exception:
                self._logger.error(exception)
                return
            self._logger.info(
                f"Current release for tag {self._tag_name} updated with app {self._app_name} version: {self._app_version}"
            )
        else:
            response = self._create_release()
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as exception:
                self._logger.error(exception)
                return
            self._logger.info(f"New release created for tag {self._tag_name}")


def main():
    parser = argparse.ArgumentParser(
        description="GitLab release manager that help to create and update release for a project."
    )
    parser.add_argument(
        "-p",
        "--process",
        type=str,
        nargs=4,
        metavar=("project_id", "tag_name", "app_name", "app_version"),
        default=None,
        help="¨Process a release based on a tag.",
    )
    args = parser.parse_args()
    if args.process:
        gitlab_release_manager = GitlabReleaseManager(
            args.process[0],
            args.process[1],
            args.process[2],
            args.process[3],
        )
        gitlab_release_manager.process_release()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
