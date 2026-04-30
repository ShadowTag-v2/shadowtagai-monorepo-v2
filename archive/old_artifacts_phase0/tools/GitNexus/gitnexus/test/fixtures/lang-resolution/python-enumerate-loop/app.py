from user import User


def process_users(users: dict[str, User]):
    # 3-variable enumerate: i=index, k=key, v=value (User)
    for _i, _k, v in enumerate(users.items()):
        v.save()


def process_nested_tuple(users: dict[str, User]):
    # Nested tuple pattern: i=index, (k,v) tuple unpacked
    for _i, (_k, v) in enumerate(users.items()):
        v.save()


def process_parenthesized_tuple(users: list[User]):
    # Parenthesized tuple as top-level pattern
    for _i, u in enumerate(users):
        u.save()
