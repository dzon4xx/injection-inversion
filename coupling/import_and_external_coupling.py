# Import coupling
import os


def show_os_env():
    print(os.environ)


# External coupling
import requests


def get_todo_title(id_):
    return requests.get(f"https://jsonplaceholder.typicode.com/todos/{id_}").json()[
        "title"
    ]
