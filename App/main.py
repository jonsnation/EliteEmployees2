import os
from flask import Flask, render_template
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from celery import Celery
from App.database import init_db
from App.config import load_config
from .import config 
from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views

def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
  app = Flask(__name__, static_url_path='/static')
  app.config.from_object(config)
  load_config(app, overrides)
  CORS(app)
  add_auth_context(app)
  photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
  configure_uploads(app, photos)
  add_views(app)
  init_db(app)
  celery = Celery( #celery to test an evaluate when everything is sorted
      app.import_name,
      backend=app.config['CELERY_RESULT_BACKEND'],
      broker=app.config['CELERY_BROKER_URL']
  )
  celery.conf.update(app.config)
  jwt = setup_jwt(app)

  @jwt.invalid_token_loader
  @jwt.unauthorized_loader
  def custom_unauthorized_response(error):
      return render_template('401.html', error=error), 401

  app.app_context().push()
  return app

    

