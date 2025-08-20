from flask import Flask

from src.routes import *

app = Flask(__name__, template_folder="src/templates")
app.register_blueprint(app_routes)

if __name__ == "__main__":
    app.run()
