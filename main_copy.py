import os
import re
import time
from string import letters
import random
import hashlib
import hmac
import jinja2
import webapp2
from users import *
from comment import *
from likes import *
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

#  Secret Salt
SECRET = 'imsosecret'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

#  Blog Handler
class BlogHandler(webapp2.RequestHandler):
    
    #  Functions used to render a HTML Page
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #  Used to create the secure cookie
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    #  Used to read the data stored in the secure cookie
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    #  Login function used to login the user by creating a secure cookie
    #  through calling set secure cookie function.
    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))
        
    #  Logout function used to logout user by deleting the user-id from the stored cookie.
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and Users.by_id(int(uid))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

 
#  Database model for the blog posts
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    author = db.StringProperty()
    author_uid = db.StringProperty()
    likes = db.IntegerProperty(default = 0)
    likes_list = db.StringProperty()
    post_id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    #  Used to render the new line inputs by the user and translate them as breaks
    #  so the HTML is interpreted correctly by the web browser.
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

#  Front Page of the Blog    
class BlogFront(BlogHandler):
    '''Blog Front class is the front page where all the blog posts made by
    users is posted.'''
    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts = posts, username = self.user)

class PostPage(BlogHandler):
    '''Post Page class used to show the individual post the user
    submitted to the blog. Along with comments on the post by other users.'''
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        comments = Comment.all().order('-created').filter('post_id =', int(post_id))
        post_likes = post.likes

        username = self.user

        liked = None
        if self.user:
            liked = db.GqlQuery("SELECT * FROM Like WHERE user = :1 AND post_id = :2", username, int(post_id)).get()
            # Like.all().filter('post_id =', int(post_id)).filter('user =', self.user)
        
        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post, post_id = int(post_id), post_likes = post_likes,
                    liked = liked, comments = comments, username = self.user)

    def post(self, post_id):
        # post_id = self.request.get("post")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # User clicks like button
        if self.request.get("like"):
            #  User liked post
            if post and self.user:
                post.likes += 1
                like = Like(post_id = int(post_id), user = self.user)
                like.put()
                post.put()
                time.sleep(0.2)
            self.redirect("/blog/%s" % post_id)
        # User clicks unlike button   
        elif self.request.get("unlike"):
            #  User unliked post
            if post and self.user:
                post.likes -= 1
                like = db.GqlQuery("SELECT * FROM Like WHERE post_id = :1 AND user = :2", int(post_id), self.user)
                key = like.get()
                key.delete()
                # key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                # post = db.get(key)
                # post.delete()
                post.put()
                time.sleep(0.2)
            self.redirect("/blog/%s" % post_id)
        # User enters in a comment
        else:
            content = self.request.get('content')
            # Only allow comments that have content, no empty comments        
            if content:
                c = Comment(
                        parent = blog_key(),
                        content = content,
                        post_id = int(post_id),
                        author = self.user
                        )
                c.put()
            self.redirect('/blog/%s' % str(post.key().id()))

class EditPostPage(BlogHandler):
    '''EditPost Page is used to edit an existing blog post by
    its original author.'''
    def get(self):
        post_id = self.request.get("post")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("edit-post.html", post = post, username = self.user)

    def post(self):
        if not self.user:
            self.redirect('/login')
            
        # Retrieve the user's input from the form
        subject = self.request.get('subject')
        content = self.request.get('content')
        a = self.request.cookies.get('user_id')
        uid = check_secure_val(a)
        author = Users.by_id(int(uid))

        # Obtain the exact post that the user wants to edit
        post_id = self.request.get("post")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # Finish the edit to the post if there is a subject and/or content. Otherwise, ask the user to enter a subject and/or content.
        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content, please!"
            self.render("edit-post.html", subject=subject, content=content, error=error)

class DeletePostPage(BlogHandler):
    '''DeletePost Page is used to delete a user's blog posts from
    the Blog's database.'''
    def get(self):
        self.render("delete-post.html", username = self.user)

    def post(self):
        if not self.user:
            return self.redirect('/blog')

        # Delete the users post from the Post DB
        post_id = self.request.get("post")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        post.delete()
        self.redirect('/blog')
                          
class NewPost(BlogHandler):
    '''New Post class used to create a new blog post on the blog using a form
    that requires a subject and content.'''
    def get(self):
        if self.user:
            self.render("newpost.html", username = self.user)
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            return self.redirect('/blog')

        # Retrieve the user's input from the form
        subject = self.request.get('subject')
        content = self.request.get('content')
        a = self.request.cookies.get('user_id')
        uid = check_secure_val(a)
        author = Users.by_id(int(uid))
        
        # Store the blog post in the database if there New Post form was filled out.
        # Otherwise, give them an error and ask to re-enter in the fields again.
        if subject and content:
            p = Post(
                parent = blog_key(),
                subject = subject,
                content = content,
                author = author,
                author_uid = str(uid),
                likes = 0)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

# # # # #  end of blog stuff  # # # # # 


class Signup(BlogHandler):   
    '''Signup Class used to handle the signup page form by extracting the credentials
    of the user and giving feedback on whether those credentials are correct.'''
    def get(self):
        self.render("signup-form.html")
    def post(self):
        # Form Error variable
        have_error = False
        
        # New Users crendentials
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        # Error checking of the signup form data. Checks for
        # valid username, password, email, and if the user exists already.
        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if existing_user(self.username):
            params['error_username'] = "That username is already exists, select a different one."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True
             
        # self.response.headers.add_header('Set-Cookie', 'user=%s' % str(self.username)) ---TEST CODE

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    '''Register Class used to input the new user in the database
    and login them into the blog site.'''
    def done(self):
        u = Users.register(self.username, self.password, self.email)
        u.put()

        self.login(u)        
        self.redirect('/blog')

class Login(BlogHandler):
    '''Login Class for users that have been registered already.'''
    def get(self):
        self.render('login-form.html')
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = Users.login(username, password)

        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    '''Logout Class used to logout the user from the blog website'''
    def get(self):
        self.logout()
        self.redirect('/login')
        
class Welcome(BlogHandler):
    '''Welcome Class used to display the welcome page to a new user.'''
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user)
        else:
            self.redirect('/signup')

class NewPassword(BlogHandler):
    '''Change the password of an existing user'''
    def get(self):
        self.render('change-password-form.html')
    def post(self):
        # Re-submit the user's credentials back in the Users DB and log them in.
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')

        u = Users.login(self.username, self.password)

        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)            
        
app = webapp2.WSGIApplication([('/', BlogFront),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/edit?', EditPostPage),
                               ('/blog/delete?', DeletePostPage)
                               ],
                              debug=True)
