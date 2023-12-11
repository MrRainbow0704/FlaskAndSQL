from flask import Flask
import config

app = Flask(__name__, root_path=config.ROOT_DIR)

from . import routes
