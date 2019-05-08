import os

import flask

from gogdb import app


@app.route("/sitemap.xml")
def robots():
    static_path = os.path.join(app.root_path, "static")
    return flask.send_from_directory(
        static_path, "sitemap.xml", mimetype="text/xml")
