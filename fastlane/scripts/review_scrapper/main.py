# main.py

import optparse
from misc import config
import ios_review
import android_review
from misc.utils import build_json_result

if __name__ == "__main__":
    options = optparse.OptionParser(usage="%prog [options]", description="gSender")

    options.add_option("-i", "--ios", action="store_true", dest="ios", help="scrapping ios review")
    options.add_option("-a", "--android", action="store_false", dest="ios", help="scrapping android review")
    options.add_option("-k", "--key", type="str", default="KEY", help="key needed for google store")
    options.add_option("-p", "--package", type="str", default="com.fortuneo.android", help="package name of the app")
    options.add_option("-f", "--file", type="str", default="reviews.json", help="filename output")
    options.add_option("-t", "--treshold", type="int", default=3, help="fetch reviews from x hours old")

    opts, args = options.parse_args()
    reviews = []

    if opts.ios:
        print("Fetching iOs reviews.")
        reviews = ios_review.get_ios_reviews(package=config.IOS_PACKAGE_NAME, opts.key)
    else:
        print("Fetching Android reviews.")
        reviews = android_review.get_android_reviews(package=config.ANDROID_PACKAGE_NAME, auth_key=opts.key)

    with open(config.OUTPUT_FILE, 'w') as file:
        file.write(build_json_result(reviews=reviews))
