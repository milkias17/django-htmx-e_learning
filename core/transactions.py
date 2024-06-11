from chapa import Chapa
from dotenv import dotenv_values

config = dotenv_values()
SECRET_KEY = config.get("CHAPA_SECRET_KEY")

chapa = Chapa(SECRET_KEY)
