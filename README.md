Udacity Multi-User Blog Project
By AdamH


This is a project created through Udacity's Full Stack Nanodegree to have an intro to backend web developement programming. The project consists of a multi-user blog where users can sign in to create posts or comment on other posts as well as like other user's posts. This Multi-user Blog will combine the coding skills of python to execute the front-end actions and GQL (Google's Query Language) to perform saving/exchange of data in the backend. This site will be hosted on Google App Engine.

Check out live version here:
http://multi-userblog.appspot.com/

Technlogies Used:

Python 2.7

Bootstrap

Google App Engine

Project Specifications:

Blog must include the following features:

    Front page that lists blog posts.
    A form to submit new entries.
    Blog posts have their own page.

Registration must include the following features:

    A registration form that validates user input, and displays the error(s) when necessary.
    After a successful registration, a user is directed to a welcome page with a greeting, “Welcome, name” where name is a name set in a cookie.
    If a user attempts to visit a restricted page without being signed in (without having a cookie), then redirect to the Signup page.

Login must include the following features:

    Have a login form that validates user input, and displays the error(s) when necessary.

Users must include the following features:

    Users should only be able to edit/delete their posts. They receive an error message if they disobey this rule.
    Users can like/unlike posts, but not their own. They receive an error message if they disobey this rule.
    Users can comment on posts. They can only edit/delete their own posts, and they should receive an error message if they disobey this rule.

Code must conform to the Python Style Guide https://www.python.org/dev/peps/pep-0008/

Setting up your computer:

    Install Python if necessary.
    Install Google App Engine SDK.
    Open GoogleAppEngineLauncher.
    Sign Up for a Google App Engine Account.
    Create a new project in Google’s Developer Console using a unique name.
    Create a new project from the file menu and choose this project's folder.
    Deploy this project by pressing deploy in GoogleAppEngineLauncher.
    When developing locally, click “Run” in GoogleAppEngineLauncher and visit localhost:Port in your favorite browser, where Port is the number listed in GoogleAppEngineLauncher’s table under the column Port.
