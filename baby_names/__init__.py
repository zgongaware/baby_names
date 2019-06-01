from flask import Flask

app = Flask(__name__)

from baby_names import routes
