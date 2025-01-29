import os
import argparse
import requests


class GitlabTagsManager:
    def __init__(self, tag_name, project_id):
        self.gitlab_api_token = os.environ.get("KS739_API_TOKEN")
        self.project_id = project_id
        self.tag_name = tag_name

    def protect_tag(self):
        headers = {"PRIVATE-TOKEN": self.gitlab_api_token}
        response = requests.post(
            f"https://gitlark.s.arkea.com/api/v4/projects/{self.project_id}/protected_tags?name={self.tag_name}",
            headers=headers,
        )
        print(response.content)


def main():
    parser = argparse.ArgumentParser(
        description="GitLab tags manager that help to manipulate tags."
    )
    parser.add_argument(
        "-p",
        "--protect_tag",
        type=str,
        nargs=2,
        metavar=("tag_name", "project_id"),
        default=None,
        help="Process a release based on a tag.",
    )
    args = parser.parse_args()
    if args.protect_tag:
        gitlab_tags_manager = GitlabTagsManager(
            args.protect_tag[0],
            args.protect_tag[1],
        )
        gitlab_tags_manager.protect_tag()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
