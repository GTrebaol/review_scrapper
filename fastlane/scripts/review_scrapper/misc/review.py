# review.py

import json
from datetime import datetime


class Review:
    def __init__(self, os, author_name, title, rating, content, datetime, version, build_version, phone, truncated_comment):
        self.os = os
        self.author_name = author_name
        self.rating = rating
        self.content = content
        self.truncated_comment = truncated_comment
        self.datetime = datetime
        self.title = title
        self.version = version
        self.build_version = build_version
        self.phone = phone

    def to_json(self):
        serializable_object = self
        serializable_object.datetime = str(serializable_object.datetime)
        return json.dumps(
            serializable_object,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )
