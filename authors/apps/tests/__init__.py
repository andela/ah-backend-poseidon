new_user = {
    "user": {
        "username": "Jac",
        "email": "jak@jake.jake",
        "password": "jakejake"
    }
}

new_user_2 = {
    "user": {
        "username": "John",
        "email": "john@dev.com",
        "password": "johnadmin"
    }
}

dup_username = {
    "user": {
        "username": "Jac",
        "email": "jake2@jake.jake",
        "password": "jakejake"
    }
}

data2 = {
    "user": {
        "username": "Jacko",
        "email": "jak@jake.jake",
        "password": "jakejake"
    }
}

invalid_email = {
    "user": {
        "username": "Jac",
        "email": "jakjake",
        "password": "jakejake"
    }
}

invalid_password = {
    "user": {
        "username": "Jac",
        "email": "jak@jake.com",
        "password": "jake@@$#$%"
    }
}

short_password = {
    "user": {
        "username": "Jac",
        "email": "jak@jake.com",
        "password": "jake"
    }
}

user_login = {"user": {"username": "Jac", "password": "jakejake"}}
post_article = {
    "article": {
        "title": "Who is he",
        "description": "He has a bald head",
        "body": "He has ruled Uganda for over 30 years",
        "tags": ["about", "politics"]
    }
}
post_article_2 = {
    "article": {
        "title": "Pythonistas",
        "description": "Python lovers' life",
        "body": "I talk about who the life of pythonistas",
        "tags": ["python", "technology", "programming"]
    }
}
update_article = {
    "article": {
        "title": "Who is he and why is he here",
        "description": "He has a bald head",
        "body": "He has ruled Uganda for over 30 years",
        "tags": ["life"]
    }
}
article_missing_data = {
    "article": {
        "description": "He has a bald head",
        "body": "He has ruled Uganda for over 30 years"
    }
}


comment = {"comment": {
    "body": "This is a comment",
}}

thread = {"comment": {
    "body": "This is a comment"
}}


ARTICLE_URL = '/api/articles'
