"""
Module to handle test data and functions
"""


class TestData:

    post_article = {
        "article": {
            "title": "Who is he",
            "description": "He has a bald head",
            "body": "He has ruled Uganda for over 30 years"
        }
    }
    update_article = {
        "article": {
            "title": "Who is he and why is he here",
            "description": "He has a bald head",
            "body": "He has ruled Uganda for over 30 years"
        }
    }
    article_missing_data = {
        "article": {
            "description": "He has a bald head",
            "body": "He has ruled Uganda for over 30 years"
        }
    }
