from flask import Flask

app = Flask(__name__, static_folder='static')

from controllers.app_controller import *

if __name__ == '__main__':
    app.run(debug=True)
