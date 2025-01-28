import requests
import os


def download_artifacts():
    """Download all artifacts of a previous Bitrise build.
    For this, we use global variables set by the CI:
        PREVIOUS_APP_SLUG: The app slug of the previous build.
        PREVIOUS_BUILD_SLUG: The build slug of the previous build.
        BITRISE_USER_TOKEN: The token used to access to the Bitrise API.
    """
    previous_app_slug = os.environ.get("PREVIOUS_APP_SLUG")
    previous_build_slug = os.environ.get("PREVIOUS_BUILD_SLUG")
    bitrise_user_token = os.environ.get("BITRISE_USER_TOKEN")
    url = "https://api.bitrise.io/v0.1/apps/{}/builds/{}/artifacts".format(
        previous_app_slug, previous_build_slug
    )
    headers = {"Accept": "application/json", "Authorization": bitrise_user_token}
    response = requests.get(url, headers=headers)
    artifacts = response.json()
    for data in artifacts["data"]:
        download_artifact(
            previous_app_slug, previous_build_slug, bitrise_user_token, data["slug"]
        )
    while "next" in artifacts["paging"]:
        url = "https://api.bitrise.io/v0.1/apps/{}/builds/{}/artifacts?next={}".format(
            previous_app_slug, previous_build_slug, artifacts["paging"]["next"]
        )
        headers = {"Accept": "application/json", "Authorization": bitrise_user_token}
        response = requests.get(url, headers=headers)
        artifacts = response.json()
        for data in artifacts["data"]:
            download_artifact(
                previous_app_slug, previous_build_slug, bitrise_user_token, data["slug"]
            )


def download_artifact(
    previous_app_slug: str,
    previous_build_slug: str,
    bitrise_user_token: str,
    artifact_slug: str,
):
    """Download one artifact of a previous build.
    :param previous_app_slug: The app slug of the previous build.
    :param previous_build_slug: The build slug of the previous build.
    :param bitrise_user_token: The token used to access to the Bitrise API.
    :param artifact_slug: The artifact slug of an artifact in a previous build.
    """
    bitrise_deploy_dir_path = os.environ.get("BITRISE_DEPLOY_DIR")
    url = "https://api.bitrise.io/v0.1/apps/{}/builds/{}/artifacts/{}".format(
        previous_app_slug, previous_build_slug, artifact_slug
    )
    headers = {"Accept": "application/json", "Authorization": bitrise_user_token}
    response = requests.get(url, headers=headers)
    artifact = response.json()
    title = artifact["data"]["title"]
    download_artifact_url = artifact["data"]["expiring_download_url"]
    print("Downloading {}".format(title))
    response = requests.get(download_artifact_url)
    if not os.path.exists(bitrise_deploy_dir_path):
        os.makedirs(bitrise_deploy_dir_path)
    artifact_path = os.path.expanduser("{}/{}".format(bitrise_deploy_dir_path, title))
    open(artifact_path.format(bitrise_deploy_dir_path, title), "wb").write(
        response.content
    )


download_artifacts()
