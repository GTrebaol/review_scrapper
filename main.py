# main.py

import optparse
from misc.config import config
import ios_review
import android_review
from misc.utils import build_json_result

"""
# Génération d'un fichier json contenant les notes et commentaires store des applications android et ios
Les variables d'environnement nécéssairse en fonction de l'os sont les suivantes : 

iOs :
    KEY_ID: identifiant de clef API Store connect (onglet users de l'app store connect)
    ISSUER_ID:  identifiant emetteur jeton d'authent (onglet users de l'app store connect)
    PRIVATE_KEY:    clef sous format (--------- BEGIN PRIVATE KEY --------)
    REPO_PACKAGE_NAME:  identifiant de l'application (https://appstoreconnect.apple.com/apps/XXXXXXXX)
Android:
    JSON_KEY_DATA: clef privée générée dans Google Cloud
    REPO_PACKAGE_NAME: nom de package de l'app (com.fortuneo.android par exemple)
    
Optionnelles : 
    OUTPUT_FILE: fichier de sortie contenant les données
    TIMEDELTA_HOURS: plage horaire de récupération des notes et commentaires (voir check_datetime_treshold)

"""
if __name__ == "__main__":
    options = optparse.OptionParser(usage="%prog [options]", description="gSender")

    options.add_option("-i", "--ios", action="store_true", dest="ios", help="scrapping ios review")
    options.add_option("-a", "--android", action="store_false", dest="ios", help="scrapping android review")

    opts, args = options.parse_args()
    reviews = []

    if opts.ios:
        print("Fetching iOs reviews.")
        reviews = ios_review.get_reviews()
    else:
        print("Fetching Android reviews.")
        reviews = android_review.get_reviews()

    with open(config.OUTPUT_FILE, 'w') as file:
        file.write(build_json_result(reviews=reviews))
