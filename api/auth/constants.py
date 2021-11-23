SUPERUSERS = [1]
GUEST_IDS = [3]
TESTING = True  # Uses benign heating system when True
# API will fail if no heating system in place when False

origins = ["https://example.app"]

origins = origins + ["*"] if TESTING else origins
SECRET_KEY = "SoMeThInG_-sUp3Rs3kREt!!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 5
