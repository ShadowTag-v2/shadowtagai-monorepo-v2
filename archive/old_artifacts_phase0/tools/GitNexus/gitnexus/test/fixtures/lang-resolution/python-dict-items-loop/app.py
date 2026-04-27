from user import User


def process(data: dict[str, User]):
    for _key, user in data.items():
        user.save()
