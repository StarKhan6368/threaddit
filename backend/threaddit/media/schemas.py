import re

FILE_NAME_REGEX = re.compile(r"^[\w\s-]+\.\w{3,}$")
MEDIA_URL_REGEX = re.compile(r"^(https?:\/\/)?(www\.)?([\w.]+\.\w+).*\/([\w\s-]+\.\w{3,})$")
