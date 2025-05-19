import argparse
import json
import logging
import os
import re
import subprocess

import requests

logging.basicConfig(level=logging.INFO)


class InstanaManager:
    """A manager used to process stuff related to mobile apps and Instana."""

    MAX_FILE_SIZE = 9  # Size in MB
    # By default use instana.rec configuration
    INSTANA_CONFIGURATION = {
        "instana_url": "https://horsprod-apmarkea.instana.io",
        "instana_api_token": os.environ.get("INSTANA_HP_API_TOKEN"),
    }

    def __init__(self) -> None:
        pass

    def split_file(self, working_dir, file_name):
        """Split a given file to subfiles of 9MB.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            file_name (str): The debug symbols file name.
        """
        file_path = os.path.join(working_dir, f"{file_name}.tgz")
        if os.path.getsize(file_path) / (1024 * 1024) < self.MAX_FILE_SIZE:
            logging.info("File size is within the allowed limit, skipping split.")
            return
        subprocess.run(
            [
                "split",
                "-b",
                f"{self.MAX_FILE_SIZE}m",
                f"{working_dir}/{file_name}.tgz",
                f"{working_dir}/{file_name}.tgz_blob_",
            ]
        )

    def upload_file(
            self,
            working_dir,
            file_name,
            file_id,
            file_type,
            config_id,
            sourcemap_upload_id,
    ):
        """Upload subfiles of 9MB to a given Instana project.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            file_name (str): The debug symbols file name.
            file_id (str): _description_
            file_type (str): R8PG_MAP for android and dSYM for iOS.
            config_id (str): Instana project key.
            sourcemap_upload_id (str): Stack trace translation ID of the project.
        """
        splitted_file_number = 1  # The index starts from 1, not 0
        api_token = self.INSTANA_CONFIGURATION.get("instana_api_token")
        headers = {
            "authorization": f"apiToken {api_token}",
        }
        for working_dir_file_name in sorted(os.listdir(working_dir)):
            if re.compile(f"^{file_name}.tgz_blob_").match(working_dir_file_name):
                files = {
                    "fileId": (None, f"{file_id}"),
                    "fileType": (None, f"{file_type}"),
                    "fileFormat": (None, "tgz"),
                    "blobIndex": (None, splitted_file_number),
                    "sourceMap": open(f"{working_dir}/{working_dir_file_name}", "rb"),
                }
                instana_url = self.INSTANA_CONFIGURATION.get("instana_url")
                response = requests.put(
                    f"{instana_url}/api/mobile-app-monitoring/config/{config_id}/sourcemap-upload/{sourcemap_upload_id}/form",
                    headers=headers,
                    files=files,
                )
                logging.info(
                    f"upload_file {working_dir_file_name}: {response.status_code}"
                )
                splitted_file_number += 1

    def commit_upload_file(self, file_id, file_type, config_id, sourcemap_upload_id):
        """Finish the uploading by commiting to the Instana project.

        Args:
            file_id (str): _description_
            file_type (str): R8PG_MAP for android and dSYM for iOS.
            config_id (str): Instana project key.
            sourcemap_upload_id (str): Stack trace translation ID of the project.
        """
        api_token = self.INSTANA_CONFIGURATION.get("instana_api_token")
        headers = {
            "authorization": f"apiToken {api_token}",
        }
        files = {
            "fileId": (None, f"{file_id}"),
            "fileType": (None, f"{file_type}"),
        }
        instana_url = self.INSTANA_CONFIGURATION.get("instana_url")
        response = requests.put(
            f"{instana_url}/api/mobile-app-monitoring/config/{config_id}/sourcemap-upload/{sourcemap_upload_id}/commit",
            headers=headers,
            files=files,
        )
        logging.info(f"commit_upload_dsyms: {response.status_code}")

    def process_file(
            self,
            working_dir,
            file_name,
            file_id,
            file_type,
            config_id,
            sourcemap_upload_id,
    ):
        """Upload debug symbols to an Instana project.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            file_name (str): The debug symbols file name.
            file_id (str): _description_
            file_type (str): R8PG_MAP for android and dSYM for iOS.
            config_id (str): Instana project key.
            sourcemap_upload_id (str): Stack trace translation ID of the project.
        """
        self.split_file(working_dir, file_name)
        self.upload_file(
            working_dir,
            file_name,
            file_id,
            file_type,
            config_id,
            sourcemap_upload_id,
        )
        self.commit_upload_file(file_id, file_type, config_id, sourcemap_upload_id)

    def process_data(self,
                     data_type,
                     app,
                     timeframe
                     ):
        """Fetch data and build a json file depending on the metrics wanted

        Args:
            data_type (str): type of instana data needed (crash_list only atm)
            app (str): Instana mobile app name
            timeframe (str): windows size of the data wanted in ms (one hour = 3600000)
        """
        if data_type == "crash_list":
            self.process_data_crash_list(app, timeframe)
        else:
            logging.info("Data type inconnu (crash_list")

    def process_data_crash_list(self,
                                app_name,
                                timeframe):
        """Fetch top crash list of a given mobile app

        Args:
            app_name (str): Instana mobile app name
            timeframe (str): windows size of the data wanted in ms (one hour = 3600000)
        """

        app_id = self.get_instana_app_id(app_name)
        url_crash = self.INSTANA_CONFIGURATION.get(
            "instana_url") + f"/#/mobileAppMonitoring/mobileApp;mobileAppId={app_id}/crashes"
        with open(os.path.dirname(__file__) + "/json/get_crash_list.json") as file:
            json_str = file.read()
            json_str = json_str.replace('"#timeFrame#"', timeframe)
            json_str = json_str.replace('#appName#', app_name)

        response = self.call_instana_metrics(json_str).json()
        top_crashes = sorted(
            response["items"],
            key=lambda x: x["metrics"]["beaconCount.sum"][0][1],
            reverse=True
        )[:5]
        with open("crashes.json", "w") as file:
            message = '{ "crashes" :' + json.dumps(
                top_crashes) + ', "url": "' + url_crash + '", "appName": "' + app_name + '"}'
            logging.info(message)
            file.write(message)

    def call_instana_metrics(self, data):
        """Make a request on the beacon-groups of instana

        Args:
            data (dict): data json payload
        """
        url = "/api/mobile-app-monitoring/analyze/beacon-groups"
        return self.call_instana_post(self.get_json_header(), url, data)

    def call_instana_post(self, headers, url, data):
        """Make a POST request to Instana

        Args:
            headers (dict): headers dict
            url (str): url wanted without the instana base path
            data (dict): data json payload
        """

        call_url = self.INSTANA_CONFIGURATION.get("instana_url") + url
        try:
            response = requests.post(call_url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during POST request: {e}")
            return None
        logging.info(f"call_instana_post {url}: {response.status_code}")
        return response

    def call_instana_get(self, headers, url):
        """Make a GET request to Instana

        Args:
           headers (dict): headers dict
           url (str): url wanted without the instana base path
        """
        call_url = self.INSTANA_CONFIGURATION.get("instana_url") + url
        try:
            response = requests.get(call_url, headers=headers)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during POST request: {e}")
            return None
        logging.info(f"call_instana_get {url}: {response.status_code}")
        return response

    def get_instana_app_id(self, app_name):
        """Get instana mobile app ID from its name

        Args:
           app_name (str): displayed app name
        """
        url = "/api/mobile-app-monitoring/config"
        response = self.call_instana_get(self.get_json_header(), url)
        data = response.json()
        app_id = None
        if len(data) > 0:
            for item in data:
                if item['name'] == app_name:
                    app_id = item['id']
        return app_id

    def get_json_header(self):
        """Get json header for instana calls"""
        api_token = self.INSTANA_CONFIGURATION.get("instana_api_token")
        return {
            "authorization": f"apiToken {api_token}",
            "Content-Type": "application/json"
        }


class IosInstanaManager(InstanaManager):
    """A manager used to process stuff related to iOS apps and Instana.

    Args:
        InstanaManager (): A manager used to process stuff related to mobile apps and Instana.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def zip_to_tgz(working_dir, dsyms_name):
        """Transform zip file to tgz file.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            dsyms_name (str): The dSYM content to upload.
        """
        if not dsyms_name.endswith(".zip"):
            dsyms_name.join(".zip")
        if not os.path.exists(f"{working_dir}/{dsyms_name}"):
            logging.error(f"File not found: {working_dir}/{dsyms_name}")
            return
        subprocess.run(
            [
                "unzip",
                "-q",
                f"{working_dir}/{dsyms_name}",
                "-d",
                f"{working_dir}/unzipped",
            ]
        )
        subprocess.run(
            [
                "tar",
                "-czf",
                f"{working_dir}/{dsyms_name}.tgz",
                f"{working_dir}/unzipped",
            ]
        )

    def process_dsyms(
            self,
            working_dir,
            file_name,
            file_id,
            config_id,
            sourcemap_upload_id,
    ):
        """Upload dSYM files to an Instana project.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            file_name (str): The debug symbols file name.
            file_id (str): _description_
            config_id (str): Instana project key.
            sourcemap_upload_id (str): Stack trace translation ID of the project.

        """
        self.zip_to_tgz(working_dir, file_name)
        super().process_file(
            working_dir,
            file_name,
            file_id,
            "dSYM",
            config_id,
            sourcemap_upload_id,
        )


class AndroidInstanaManager(InstanaManager):
    """A manager used to process stuff related to android apps and Instana.

    Args:
        InstanaManager (): A manager used to process stuff related to mobile apps and Instana.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def mapping_file_to_tgz(working_dir, file_name):
        """Transform mapping file to tgz.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            file_name (str): The debug symbols file name.
        """
        subprocess.run(
            [
                "tar",
                "-czf",
                f"{working_dir}/{file_name}.tgz",
                f"{working_dir}/{file_name}.txt",
            ]
        )

    def process_r8pg_map(
            self,
            working_dir,
            file_name,
            file_id,
            config_id,
            sourcemap_upload_id,
    ):
        """Upload mapping file to an Instana project.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            file_name (str): The debug symbols file name.
            file_id (str): _description_
            config_id (str): Instana project key.
            sourcemap_upload_id (str): Stack trace translation ID of the project.
        """
        self.mapping_file_to_tgz(working_dir, file_name)
        super().process_file(
            working_dir,
            file_name,
            file_id,
            "R8PG_MAP",
            config_id,
            sourcemap_upload_id,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Instana manager for crashes management of apps"
    )
    parser.add_argument(
        "-ua",
        "--upload_android",
        type=str,
        nargs=5,
        metavar=(
            "working_dir",
            "file_name",
            "file_id",
            "config_id",
            "sourcemap_upload_id",
        ),
        default=None,
        help="Process mapping files to upload them on Instana.",
    )
    parser.add_argument(
        "-ui",
        "--upload_ios",
        type=str,
        nargs=5,
        metavar=(
            "working_dir",
            "file_name",
            "file_id",
            "config_id",
            "sourcemap_upload_id",
        ),
        default=None,
        help="Process dsym files to upload them on Instana.",
    )
    parser.add_argument(
        "-p",
        "--production",
        action="store_true",
        default=False,
        help="Will run for production environment",
    )
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        nargs=3,
        metavar=(
            "data_type",
            "app_name",
            "timeframe"
        ),
        default=None,
        help="Get data about given app name (crash_list only atm)",
    )
    args = parser.parse_args()
    if args.production:
        InstanaManager.INSTANA_CONFIGURATION.update(
            {
                "instana_url": "https://prod-arkea.instana.io",
                "instana_api_token": os.environ.get("INSTANA_PROD_API_TOKEN"),
            }
        )

    if args.upload_android is not None:
        android_instana_manager = AndroidInstanaManager()
        android_instana_manager.process_r8pg_map(
            args.upload_android[0],
            args.upload_android[1],
            args.upload_android[2],
            args.upload_android[3],
            args.upload_android[4],
        )
    elif args.upload_ios is not None:
        ios_instana_manager = IosInstanaManager()
        ios_instana_manager.process_dsyms(
            args.upload_ios[0],
            args.upload_ios[1],
            args.upload_ios[2],
            args.upload_ios[3],
            args.upload_ios[4],
        )
    elif args.data is not None:
        instana_manager = InstanaManager()
        instana_manager.process_data(
            args.data[0],
            args.data[1],
            args.data[2],
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
