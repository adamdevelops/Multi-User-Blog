import re
from string import letters
import random
import hashlib
import hmac
import jinja2
import webapp2

from main import *
from google.appengine.ext import db

#Database model for the Likes of posts
class Like(db.Model):
    user = db.StringProperty()
    post_id = db.IntegerProperty(required=True)
    last_liked = db.DateTimeProperty(auto_now=True)
