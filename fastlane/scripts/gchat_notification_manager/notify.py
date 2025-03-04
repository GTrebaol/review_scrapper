from datetime import datetime
import json
import logging
import optparse
import os
import random
import string

import requests

proxy_settings = {"http": "", "https": ""}

logging.basicConfig(level=logging.INFO)


def get_text_from_file(filename: str) -> str:
    with open(filename) as f:
        result = f.read()
    return result


def generate_thread_id(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))

def convert_timestamp(timestamp_ms):
    # Convertir le timestamp en secondes
    timestamp_sec = timestamp_ms / 1000
    # Convertir en objet datetime
    date_time = datetime.fromtimestamp(timestamp_sec)
    # Formater la date en chaîne de caractères
    formatted_date = date_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date


def send_simple_message(google_chat_webhook_url: str, message: str) -> bool:
    """
    # Envoi d'un simple message texte dans un canal google chat
    :param google_chat_webhook_url: URL du webhook configuré dans le canal Google Chat
    :param message: Corps du message à poster
    :return: True si le message est posté, False si une erreur est survenue
    """
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    google_chat_message = '{"text": "%s"}' % message
    session = requests.session()
    session.proxies.update(proxy_settings)
    try:
        response = session.post(
            google_chat_webhook_url,
            google_chat_message,
            headers=message_headers,
            proxies=proxy_settings,
        )
        if str(response.status_code).startswith("2"):
            return True
        else:
            logging.error(
                f"Erreur {str(response.status_code)} {str(response.text)}. Le message n'a pas pu être posté sur Google Chat."
            )
            return False
    except requests.RequestException as e:
        logging.error(f"Impossible de poster le message sur Google Chat : {e.response}")
        return False


def send_card_message(google_chat_webhook_url: str, message_json: str):
    message_headers = {"Content-Type": "application/json"}
    session = requests.session()
    session.proxies.update(proxy_settings)
    try:
        response = session.post(
            url=google_chat_webhook_url,
            json=json.loads(message_json),
            headers=message_headers,
            proxies=proxy_settings,
        )
        if str(response.status_code).startswith("2"):
            return True
        else:
            logging.error(
                f"Erreur {str(response.status_code)}. Le message n'a pas pu être posté sur Google Chat."
            )
            logging.error(
                f"Erreur {str(response.text)}. Le message n'a pas pu être posté sur Google Chat."
            )
            return False
    except requests.RequestException as e:
        logging.error(f"Impossible de poster le message sur Google Chat : {e.response}")
        return False


def send_review_message(google_chat_webhook_url: str, filename: str):
    if not is_file_empty(filename):
        with open(filename) as file:
            result = json.loads(file.read())
            if not result or "reviews" not in result:  # Vérifie si le JSON est vide
                logging.info("Fichier vide, pas de notes à traiter")
                return True
            for review in result["reviews"]:
                thread_id = generate_thread_id(5)
                template_file = os.path.dirname(__file__) + "/template_review_ios.json"
                if review["os"] == "Android":
                    template_file = (
                            os.path.dirname(__file__) + "/template_review_android.json"
                    )
                with open(template_file) as template:
                    google_chat_json = template.read()
                    google_chat_json = google_chat_json.replace(
                        "#author#", review["author_name"]
                    )
                    google_chat_json = google_chat_json.replace(
                        "#title#", review["title"]
                    )
                    google_chat_json = google_chat_json.replace(
                        "#note#", get_star_rating(review["rating"])
                    )
                    google_chat_json = google_chat_json.replace("#color#", "#0E3C68")
                    google_chat_json = google_chat_json.replace(
                        "#version#", review["version"]
                    )
                    google_chat_json = google_chat_json.replace(
                        "#version_code#", str(review["build_version"])
                    )
                    google_chat_json = google_chat_json.replace(
                        "#phone#", review["phone"]
                    )
                    google_chat_json = google_chat_json.replace(
                        "#datetime#", review["datetime"]
                    )
                    google_chat_json = google_chat_json.replace("#threadId#", thread_id)
                    google_chat_json = google_chat_json.replace(
                        "#os_version#", review["os_version"]
                    )
                    google_chat_url = google_chat_webhook_url

                    avatar_url = "https://static.vecteezy.com/system/resources/previews/021/496/287/non_2x/ios-icon-logo-software-apple-symbol-with-name-black-design-mobile-illustration-free-vector.jpg"
                    if review["os"] == "Android":
                        avatar_url = "https://static.vecteezy.com/ti/vecteur-libre/p2/14414701-logo-android-sur-fond-transparent-gratuit-vectoriel.jpg"

                    google_chat_json = google_chat_json.replace("#avatar#", avatar_url)
                    google_chat_json = google_chat_json.replace(
                        "#content#", review["content"]
                    )
                    send_card_message(
                        google_chat_webhook_url=google_chat_url,
                        message_json=google_chat_json,
                    )
    else:
        logging.info("Fichier vide, pas de notes à traiter")

def send_crash_list_message(google_chat_webhook_url: str, filename: str):
    if not is_file_empty(filename):
        with open(filename) as file:
            result = json.loads(file.read())
            if not result :  # Vérifie si le JSON est vide
                logging.info("Fichier vide, pas de crash à traiter")
                return True

            template_file = os.path.dirname(__file__) + "/template_crash_list.json"
            with open(template_file) as template:
                google_chat_json = template.read()
                for idx, crash in enumerate(result["crashes"]):
                    google_chat_json = google_chat_json.replace(
                        f"#crash-{idx}#", crash["name"].replace('"',"'")
                    )
                    google_chat_json = google_chat_json.replace(
                        f"#earliest-{idx}#", convert_timestamp(crash["earliestTimestamp"])
                    )
                    google_chat_json = google_chat_json.replace(
                        f"#occurences-{idx}#", str(int(crash["metrics"]["beaconCount.sum"][0][1]))
                    )

                google_chat_json = google_chat_json.replace(
                    "#url-crash#", result["url"]
                )
                google_chat_json = google_chat_json.replace(
                    "#appName#", result["appName"]
                )
            send_card_message(
                google_chat_webhook_url=google_chat_webhook_url,
                message_json=google_chat_json,
            )
    else:
        logging.info("Fichier vide, pas de notes à traiter")

def get_star_rating(rating):
    result = ""
    star = "⭐"
    for i in range(int(rating)):
        result = result + star
    return result


def send_delivery_message(
        google_chat_webhook_url: str,
        title: str,
        app: str,
        branch: str,
        version: str,
        link: str,
        image_url: str,
        env: str,
        platform: str,
):
    # color by env
    if env == "REC":
        color = "#0E682F"
    elif env in {"NRG", "HML"}:
        color = "#0E3C68"
    else:
        color = "#681A0E"

    """
    Demande de message Google Chat avec card (image, titre...)
    :param google_chat_webhook_url: URL du webhook avec le chanel dans lequel il faut poster le message
    :param message: Message à poster
    :param image_url: URL du logo/ image à mettre dans l'en-tête
    :param title: Titre dans l'en-tête
    :param thread: Thread du canal dans lequel poster
    :return: Retourne True si le message a été correctement posté
    """
    template_file = os.path.dirname(__file__) + "/template_delivery.json"
    with open(template_file) as template:
        google_chat_json = template.read()
        google_chat_json = google_chat_json.replace("#title#", f"{title}")
        google_chat_json = google_chat_json.replace("#platform#", f"{platform}")
        google_chat_json = google_chat_json.replace("#color#", f"{color}")
        google_chat_json = google_chat_json.replace("#img#", f"{image_url}")
        google_chat_json = google_chat_json.replace("#app#", f"{app}")
        google_chat_json = google_chat_json.replace("#env#", f"{env}")
        google_chat_json = google_chat_json.replace("#branch#", f"{branch}")
        google_chat_json = google_chat_json.replace("#version#", f"{version}")
        google_chat_url = google_chat_webhook_url

        send_card_message(
            google_chat_webhook_url=google_chat_url, message_json=google_chat_json
        )


def is_file_empty(filepath):
    return os.stat(filepath).st_size == 0


if __name__ == "__main__":
    if os.getenv("http_proxy") != "":
        proxy_settings = {
            "http": os.getenv("http_proxy"),
            "https": os.getenv("http_proxy"),
        }

    options = optparse.OptionParser(usage="%prog [options]", description="gSender")

    options.add_option(
        "-d", "--delivery", type="str", default="false", help="is an app delivery"
    )
    options.add_option(
        "-m", "--message", type="str", default="false", help="message content"
    )
    options.add_option(
        "-w", "--webhook", type="str", default="webhook", help="webhook url"
    )
    options.add_option("-a", "--app", type="str", default="CMB", help="application")
    options.add_option("-e", "--env", type="str", default="REC", help="environment")
    options.add_option("-b", "--branch", type="str", default="Branch", help="branch")
    options.add_option("-v", "--version", type="str", default="Version", help="version")
    options.add_option(
        "-l", "--link", type="str", default="Extra link", help="Extra link"
    )
    options.add_option("-i", "--image", type="str", default="", help="add image")
    options.add_option("-p", "--platform", type="str", default="", help="add os img")
    options.add_option(
        "-f", "--file", type="str", default="", help="get text from file"
    )
    options.add_option("-r", "--review", type="str", default="false", help="thread id")
    options.add_option("-t", "--title", type="str", default="Livraison", help="title")
    options.add_option("-c", "--crash", type="str", default="false", help="thread id")

    opts, args = options.parse_args()
    if opts.delivery != "true":
        if opts.review != "false" and opts.file != "":
            send_review_message(
                google_chat_webhook_url=opts.webhook, filename=opts.file
            )
        elif opts.crash != "false" and opts.file != "":
            send_crash_list_message(
                google_chat_webhook_url=opts.webhook, filename=opts.file
            )
        else:
            message = opts.message
            send_simple_message(google_chat_webhook_url=opts.webhook, message=message)
    else:
        send_delivery_message(
            google_chat_webhook_url=opts.webhook,
            app=opts.app,
            env=opts.env,
            branch=opts.branch,
            version=opts.version,
            link=opts.link,
            title=opts.title,
            image_url=opts.image,
            platform=opts.platform,
        )
