import argparse
import os
import re
import requests
import subprocess


class InstanaManager:
    """A manager used to process stuff related to mobile apps and Instana."""

    MAX_FILE_SIZE = 9  # Size in MB
    # By default use instana.rec configuration
    INSTANA_CONFIGURATION = {
        "instana_url": "https://horsprod-apmarkea.instana.io",
        "instana_api_token": os.environ.get("INSTANA_HP_API_TOKEN"),
    }

    @staticmethod
    def __init__() -> None:
        pass

    def split_file(self, working_dir, file_name):
        """Split a given file to subfiles of 9MB.

        Args:
            working_dir (str): The working directory where to find the debug symbols file and subfiles.
            file_name (str): The debug symbols file name.
        """
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
                print(
                    f"upload_multiple_dsyms {working_dir_file_name}: {response.status_code}"
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
        print(f"commit_upload_dsyms: {response.status_code}")

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
        if not os.path.exists(f"{working_dir}/{dsyms_name}"):
            print(f"File not found: {working_dir}/{dsyms_name}")
            return
        subprocess.run(
            [
                "unzip",
                "-q",
                f"{working_dir}/{dsyms_name}",
                "-d",
                f"{working_dir}/{dsyms_name}",
            ]
        )
        subprocess.run(
            [
                "tar",
                "-czf",
                f"{working_dir}/{dsyms_name}.tgz",
                f"{working_dir}/{dsyms_name}",
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
                f"{working_dir}/{file_name}",
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
    ),
    args = parser.parse_args()
    if args.production:
        InstanaManager.INSTANA_CONFIGURATION.update(
            {
                "instana_url": "https://prod-arkea.instana.io",
                "instana_api_token": os.environ.get("INSTANA_PROD_API_TOKEN"),
            }
        )

    if args.upload_android is not None:
        filename = args.upload_android[1]
        if not filename.endswith('.txt'):
            filename = filename + ".txt"
        android_instana_manager = AndroidInstanaManager()
        android_instana_manager.process_r8pg_map(
            args.upload_android[0],
            filename,
            args.upload_android[2],
            args.upload_android[3],
            args.upload_android[4],
        )
    elif args.upload_ios is not None:
        filename = args.upload_ios[1]
        if not filename.endswith('.zip'):
            filename = filename + ".zip"
        ios_instana_manager = IosInstanaManager()
        ios_instana_manager.process_dsyms(
            args.upload_ios[0],
            filename,
            args.upload_ios[2],
            args.upload_ios[3],
            args.upload_ios[4],
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
