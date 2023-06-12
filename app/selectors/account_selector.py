
def profile(user):
    user_id = str(user.user_id)
    first_name = user.first_name
    last_name = user.last_name
    return { "data": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                }}
