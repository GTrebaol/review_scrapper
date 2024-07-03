import requests
import json
import logging
import os
import optparse


proxy_settings = {"http": "", "https": ""}


def send_simple_message(google_chat_webhook_url: str, message: str) -> bool:
    """
    # Envoi d'un simple message texte dans un canal google chat
    :param google_chat_webhook_url: URL du webhook configuré dans le canal Google Chat
    :param message: Corps du message à poster
    :return: True si le message est posté, False si une erreur est survenue
    """
    google_chat_url = google_chat_webhook_url
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    google_chat_message = '{"text": "' + message + '"}'
    session = requests.session()
    session.proxies.update(proxy_settings)
    try:
        response = session.post(
            google_chat_url,
            google_chat_message,
            headers=message_headers,
            proxies=proxy_settings,
        )
        if str(response.status_code).startswith("2"):
            return True
        else:
            logging.error(
                f"Erreur {str(response.status_code)}. Le message n'a pas pu être posté sur Google Chat."
            )
            return False
    except requests.RequestException as e:
        logging.error(f"Impossible de poster le message sur Google Chat : {e.response}")
        return False


def send_delivery_message(
        google_chat_webhook_url: str,
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
        google_chat_json = google_chat_json.replace("#platform#", f"{platform}")
        google_chat_json = google_chat_json.replace("#color#", f"{color}")
        google_chat_json = google_chat_json.replace("#img#", f"{image_url}")
        google_chat_json = google_chat_json.replace("#app#", f"{app}")
        google_chat_json = google_chat_json.replace("#env#", f"{env}")
        google_chat_json = google_chat_json.replace("#branch#", f"{branch}")
        google_chat_json = google_chat_json.replace("#version#", f"{version}")
        google_chat_json = google_chat_json.replace("#releaseNote#", f"{link}")
        print(google_chat_json)
        google_chat_url = google_chat_webhook_url
        message_headers = {"Content-Type": "application/json"}
        session = requests.session()
        session.proxies.update(proxy_settings)
        try:
            response = session.post(
                google_chat_url,
                json=json.loads(google_chat_json),
                headers=message_headers,
                proxies=proxy_settings,
            )
            if str(response.status_code).startswith("2"):
                return True
            else:
                logging.error(
                    f"Erreur {str(response.status_code)}. Le message n'a pas pu être posté sur Google Chat."
                )
                return False
        except requests.RequestException as e:
            logging.error(
                f"Impossible de poster le message sur Google Chat : {e.response}"
            )
            return False


if __name__ == "__main__":
    if os.environ.get("http_proxy") != None:
        proxy_settings = {
            "http": os.environ.get("http_proxy"),
            "https": os.environ.get("http_proxy"),
        }

    options = optparse.OptionParser(usage="%prog [options]", description="gSender")

    options.add_option("-d", "--delivery", type="str", default="false", help="is an app delivery")
    options.add_option("-m", "--message", type="str", default="false", help="message content")
    options.add_option("-w", "--webhook", type="str", default="webhook", help="webhook url")
    options.add_option("-a", "--app", type="str", default="CMB", help="application")
    options.add_option("-e", "--env", type="str", default="REC", help="environment")
    options.add_option("-b", "--branch", type="str", default="Branch", help="branch")
    options.add_option("-v", "--version", type="str", default="Version", help="version")
    options.add_option("-r", "--link", type="str", default="Extra link", help="Extra link")
    options.add_option("-i", "--image", type="str", default="", help="add image")
    options.add_option("-p", "--platform", type="str", default="", help="add os img")

    opts, args = options.parse_args()
    if opts.delivery != "true":
        send_simple_message(
            google_chat_webhook_url=opts.webhook,
            message=opts.message
        )
    else:
        send_delivery_message(
            google_chat_webhook_url=opts.webhook,
            app=opts.app,
            env=opts.env,
            branch=opts.branch,
            version=opts.version,
            link=opts.link,
            image_url=opts.image,
            platform=opts.platform,
        )
