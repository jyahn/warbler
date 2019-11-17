import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, EditProfileForm, LikesForm
from models import db, connect_db, User, Message, Like, Thread, DM

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS

    do_logout()
    return redirect("/")


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    form = LikesForm()

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    # import pdb; pdb.set_trace()
    count_likes = len(user.likes)
    msgs_ive_liked = [u.message_id for u in g.user.likes]
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages, form=form, count_likes=count_likes, msgs_ive_liked=msgs_ive_liked)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    count_likes = len(user.likes)
    return render_template('users/following.html', user=user, count_likes=count_likes)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    count_likes = len(user.likes)
    return render_template('users/followers.html', user=user, count_likes=count_likes)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    # IMPLEMENT THIS

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = EditProfileForm(obj=g.user)

    if form.validate_on_submit():
        # import pdb; pdb.set_trace()
        user = User.authenticate(g.user.username,
                                 form.password.data)

        if (user):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data
            user.header_image_url = form.header_image_url.data
            user.bio = form.bio.data
            db.session.add(user)
            db.session.commit()
            return redirect(f"/users/{g.user.id}")

        flash("Invalid credentials.", 'danger')

    return render_template("users/edit.html", form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""
    form = LikesForm()
    msg = Message.query.get(message_id)
    msgs_ive_liked = [u.message_id for u in g.user.likes]
    liked_msgs = (Like
                  .query
                  .filter(Message.user_id.in_(msgs_ive_liked))
                  .all())
    return render_template('messages/show.html', message=msg, form=form, msgs_ive_liked=msgs_ive_liked)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


@app.route('/messages/<int:message_id>/like', methods=["POST"])
def handle_message_like(message_id):
    """Handle a like/unlike of a message."""

    form = LikesForm()
    if form.validate_on_submit():
        like_to_delete = Like.query.filter_by(
            user_id=g.user.id, message_id=message_id).first()
        if (like_to_delete):
            db.session.delete(like_to_delete)
            db.session.commit()
        else:
            try:
                liked_msg = Like(user_id=g.user.id, message_id=message_id)
                db.session.add(liked_msg)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    return redirect("/")


@app.route('/users/<int:user_id>/likes')
def display_liked_msgs(user_id):
    """Displays a list of messages that a user has liked."""

    user = User.query.get_or_404(user_id)
    liked_messages = user.liked_messages
    count_likes = len(liked_messages)
    return render_template('/users/likes.html', messages=liked_messages, user=user, count_likes=count_likes)


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    # if g.user:
    #     messages = (Message
    #                 .query
    #                 .order_by(Message.timestamp.desc())
    #                 .limit(100)
    #                 .all())

    form = LikesForm()
    if g.user:
        following_ids = [u.id for u in g.user.following]

        msgs_ive_liked = [u.message_id for u in g.user.likes]

        messages = (Message
                    .query
                    .order_by(Message.timestamp.desc())
                    .filter(Message.user_id.in_(following_ids))
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages, form=form, msgs_ive_liked=msgs_ive_liked)

    else:
        return render_template('home-anon.html')


# @app.errorhandler(404)
# def page_not_found(e):
#     """404 NOT FOUND page."""

#     return render_template('404.html'), 404


##############################################################################
# Thread and DM pages


@app.route('/threads')
def list_threads():
    """Page with listing of threads."""

    threads_with_dms = DM.query.all()
    threads_with_dms_ids = [u.thread_id for u in threads_with_dms]

    threads_master = (Thread
                .query
                .filter(Thread.id.in_(threads_with_dms_ids))
                .all())

    #the threads where I'm user 1
    threads_1 = [thread for thread in threads_master if thread.user1_id == g.user.id]
    print("threasds1",threads_1)
    #the threads where I'm user 2
    threads_2 = [thread for thread in threads_master if thread.user2_id == g.user.id]
    print ("threads2", threads_2)
    #todo: fix bug where dm to self appears twice because it appears in both threads_1 and threads_2

    return render_template('threads.html', my_user1_threads=threads_1, my_user2_threads=threads_2)
    

@app.route('/threads/add/<int:user_id>', methods=["POST"])
def add_thread(user_id):
    print ("am i in here")
    """Page to add a thread. """
    # if this user id combo exists
    thread = Thread.query.filter(
        Thread.user1_id == user_id, Thread.user2_id == g.user.id).all()

    thread2 = Thread.query.filter(
        Thread.user2_id == user_id, Thread.user1_id == g.user.id).all()

    if thread:
        print ('wow')
        return redirect(f"/threads/{thread[0].id}")
        print('wow?')

    if thread2:
        print ('wow2')
        return redirect(f"/threads/{thread2[0].id}")

    # else:
    if (user_id < g.user.id):
        new_thread = Thread(user1_id=user_id, user2_id=g.user.id)
    else:
        new_thread = Thread(user1_id=g.user.id, user2_id=user_id)
    db.session.add(new_thread)
    db.session.commit()
    print('lmao')
    return redirect(f"/threads/{new_thread.id}")


@app.route('/threads/<int:thread_id>')
def show_thread(thread_id):
    print('what about here')
    """Page to see a thread. """
    thread = Thread.query.get(thread_id)
    if g.user.id == thread.user1_id or g.user.id == thread.user2_id:
        if (g.user.id == thread.user1_id):
            other_username = thread.user2.username
        else:
            other_username = thread.user1.username

        return render_template("show-thread.html", thread=thread, other_username=other_username)
    else:
        flash('Unauthorized', 'danger')
        return redirect('/')


@app.route('/threads/<int:thread_id>/dm/add', methods=["POST"])
def add_dm(thread_id):
    """adds a dm"""
    print ('am i in dm')
    thread = Thread.query.get(thread_id)
    text = request.json["text"]
    dm = DM(text=text, thread_id=thread_id, author=g.user.id)
    db.session.add(dm)
    db.session.commit()
    all_dms = [[dm.text, dm.author] for dm in thread.dms]
    return jsonify(all_dms)



##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
