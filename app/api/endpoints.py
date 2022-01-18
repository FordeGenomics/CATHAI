from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    Response,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from app.models import User
from app import db, csrf
from datetime import datetime
from app.decorators import admin_required
import os

api = Blueprint('api', __name__)

UPLOAD_DIR = "uploads/"

if not os.path.exists(UPLOAD_DIR):
  os.makedirs(UPLOAD_DIR)

@api.route("/webforms/<filename>", methods=["POST"])
@login_required
@admin_required
@csrf.exempt
def post_webform_file(filename):
  if "/" in filename:
    # Return 400 BAD REQUEST
    abort(400, "No paths allowed. Flat files only.")

  WEBFORMS_DIR=UPLOAD_DIR + "webforms/"
  if not os.path.exists(WEBFORMS_DIR):
    os.makedirs(WEBFORMS_DIR)

  with open(os.path.join(WEBFORMS_DIR, filename), "wb") as fp:
    submitted_file = request.files['file']
    submitted_file.save(os.path.join(WEBFORMS_DIR, filename))

  return "", 201