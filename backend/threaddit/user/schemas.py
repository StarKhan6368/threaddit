import re

USER_EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,6}$")
USER_NAME_REGEX = re.compile(r"^\w{3,16}$")
