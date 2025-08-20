from flask import redirect

from . import app_routes


@app_routes.route("/")
def index():
    return redirect("/analytics")
