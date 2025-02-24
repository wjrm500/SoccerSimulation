from io import BytesIO

from flask import redirect, render_template, request, send_file, session, url_for

from utils.dependencies import db

from . import general_bp


@general_bp.route("/about", methods=["GET"])
def about():
    if request.MOBILE:
        return render_template("mobile/about.html", css_files=["rest_of_website.css", "mobile.css"])
    return render_template(
        "desktop/about.html", css_files=["rest_of_website.css"], js_files=["script.js"]
    )


@general_bp.route("/contact", methods=["GET"])
def contact():
    if request.MOBILE:
        return render_template(
            "mobile/contact.html", css_files=["rest_of_website.css", "mobile.css"]
        )
    return render_template(
        "desktop/contact.html", css_files=["rest_of_website.css"], js_files=["script.js"]
    )


@general_bp.route("/download/<universe_key>")
def download(universe_key):
    universe_data = db.get_universe_grid_file(universe_key)
    if universe_data is None:
        return "Simulation data not found", 404
    attachment_filename = "universe_" + universe_key
    return send_file(BytesIO(universe_data), download_name=attachment_filename, as_attachment=True)


@general_bp.route("/clear", methods=["GET"])
def clear_session():
    session.clear()
    url = url_for("home.get_home")
    return redirect(url)
