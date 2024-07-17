import requests
import json
import logging
import os
import optparse
import random
import string


proxy_settings = {"http": "", "https": ""}

def get_text_from_file(filename: str) -> str:
    result = ""
    with open(filename) as f:
        result = f.read()
    return result

def generate_thread_id(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def send_simple_message(google_chat_webhook_url: str, message: str, threadId: str) -> bool:
    """
    # Envoi d'un simple message texte dans un canal google chat
    :param google_chat_webhook_url: URL du webhook configuré dans le canal Google Chat
    :param message: Corps du message à poster
    :return: True si le message est posté, False si une erreur est survenue
    """
    google_chat_url = google_chat_webhook_url+"&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"
    if threadId and threadId != "":
        thread_body=',"thread": {"threadKey": "%s"}' % threadId
    else:
        thread_body = ""
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    google_chat_message ='{"text": "%s" %s}' % (message, thread_body)
    print(google_chat_url)
    print(google_chat_message)
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

def send_card_message(google_chat_webhook_url: str, message_json : str):
    message_headers = {"Content-Type": "application/json"}
    session = requests.session()
    session.proxies.update(proxy_settings)
    try:
        response = session.post(
            google_chat_webhook_url+"&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
            json=json.loads(message_json),
            headers=message_headers,
            proxies=proxy_settings,
        )
        print(response)
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

def send_review_message(
        google_chat_webhook_url: str,
        filename: str
):
    with open(filename) as file:
        result = json.loads(file.read())
        for review in result["reviews"]:
            thread_id = generate_thread_id(5)
            template_file = os.path.dirname(__file__) + "/template_review.json"
            with open(template_file) as template:
                print(review)
                google_chat_json = template.read()
                google_chat_json = google_chat_json.replace("#author#", review['author_name'])
                google_chat_json = google_chat_json.replace("#note#", review['rating'])
                google_chat_json = google_chat_json.replace("#color#", "#0E3C68")
                google_chat_json = google_chat_json.replace("#version#", review['version'])
                google_chat_json = google_chat_json.replace("#version_code#", str(review['build_version']))
                google_chat_json = google_chat_json.replace("#phone#", review['phone'])
                google_chat_json = google_chat_json.replace("#threadId#", thread_id)
                google_chat_url = google_chat_webhook_url

                avatar_url = "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTPvFqD-oo4WMdikaau1qoCReBs1-aJSKEKRXubxk03-5MTDjJJ"
                if review["os"] == "Android":
                    avatar_url = "https://lh6.googleusercontent.com/proxy/NYTh9VGNYogtyxClVtgIMHkObbFxpzElxzwI1ck7RvRypoVUeuwVWy6JdOMfHb_Bo3AZcbbhaMHlD1q1TS86og8dSij4Pgp3aBs3QNPG9rBcbiuHsnZe8Gz9YADikqlv4mrAp5AnnI9FlZjdtm9ZAoHhVfUwYukRzg"

                google_chat_json = google_chat_json.replace("#avatar#", avatar_url)

                if review["truncated_comment"] != "":
                    full_comment = "Suite du commentaire : \n« " + review["content"] + " »"
                    google_chat_json = google_chat_json.replace("#comment#", review["truncated_comment"])
                    send_card_message(google_chat_webhook_url=google_chat_url, message_json=google_chat_json)
                    send_simple_message(google_chat_webhook_url=google_chat_url, message=full_comment, threadId=thread_id)
                else:
                    google_chat_json = google_chat_json.replace("#comment#", review["content"])
                    send_card_message(google_chat_webhook_url=google_chat_url, message_json=google_chat_json)



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

        send_card_message(google_chat_webhook_url=google_chat_url, message_json=google_chat_json)


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
    options.add_option("-l", "--link", type="str", default="Extra link", help="Extra link")
    options.add_option("-i", "--image", type="str", default="", help="add image")
    options.add_option("-p", "--platform", type="str", default="", help="add os img")
    options.add_option("-f", "--file", type="str", default="", help="get text from file")
    options.add_option("-r", "--review", type="str", default="false", help="thread id")

    opts, args = options.parse_args()
    if opts.delivery != "true":
        if(opts.review != "false" and opts.file != ""):
            send_review_message(google_chat_webhook_url=opts.webhook, filename=opts.file)
        elif(opts.t):
            message = opts.message
            send_simple_message(
                google_chat_webhook_url=opts.webhook,
                message=message
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
