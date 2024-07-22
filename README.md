# App Store Connect Reviews Fetcher

## Overview

This project is designed to fetch user reviews of an iOS/Android mobile app through the proper API. The script is modular, making it easy to maintain and extend.

## Project Structure


- **misc/config.py**: Contains configuration values and handles environment variables.
- **misc/review.py**: Defines the `Review` class to represent individual reviews.
- **misc/token_generator.py**: Generates the JWT token for authentication.
- **misc/utils.py**: Contains utility functions.
- **android_reviews.py**: Fetches Android reviews from the Play Store API.
- **ios_reviews.py**: Fetches iOS reviews from the App Store Connect API.
- **main.py**: The main script to execute the fetching process.

## Setup

### Prerequisites

- Python 3+
- Required Python packages: `pyjwt`, `requests`, `googleapiclient.discovery`, `google.oauth2`
  

You can install the required packages using pip:

```sh
pip install -r requirements.txt
