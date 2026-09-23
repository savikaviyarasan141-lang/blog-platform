from sqlalchemy.engine import URL
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv(override=True)
app = Flask(__name__)

# =========================
# Configuration
# =========================

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    database=os.getenv("MYSQL_DATABASE")
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "ssl": {}
    }
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)


# =========================
# Login Configuration
# =========================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =========================
# Database Models
# =========================

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="posts"
    )


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("posts.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="comments"
    )


# =========================
# Login Manager
# =========================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# =========================
# Home
# =========================

@app.route("/")
def home():

    latest_posts = Post.query.order_by(
        Post.created_at.desc()
    ).limit(3).all()

    return render_template(
        "index.html",
        latest_posts=latest_posts
    )


# =========================
# Register
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:

            flash("Username or email already exists.")

            return redirect(
                url_for("register")
            )

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. Please login."
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================
# Login
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("home")
            )

        flash(
            "Invalid email or password."
        )

    return render_template(
        "login.html"
    )


# =========================
# Logout
# =========================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# =========================
# Posts - Web Pages
# =========================

@app.route("/posts")
def posts():

    search = request.args.get(
        "q",
        ""
    ).strip()

    if search:

        all_posts = Post.query.filter(
            (Post.title.ilike(
                f"%{search}%"
            )) |
            (Post.content.ilike(
                f"%{search}%"
            ))
        ).order_by(
            Post.created_at.desc()
        ).all()

    else:

        all_posts = Post.query.order_by(
            Post.created_at.desc()
        ).all()

    return render_template(
        "posts.html",
        posts=all_posts,
        search=search
    )


# =========================
# Create Post - Web
# =========================

@app.route(
    "/create-post",
    methods=["GET", "POST"]
)
@login_required
def create_post():

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        post = Post(
            title=title,
            content=content,
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()

        return redirect(
            url_for("posts")
        )

    return render_template(
        "create_post.html"
    )


# =========================
# View Post
# =========================

@app.route(
    "/post/<int:post_id>"
)
def view_post(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    comments = Comment.query.filter_by(
        post_id=post.id
    ).order_by(
        Comment.created_at.desc()
    ).all()

    return render_template(
        "post.html",
        post=post,
        comments=comments
    )


# =========================
# Add Comment - Web
# =========================

@app.route(
    "/post/<int:post_id>/comment",
    methods=["POST"]
)
@login_required
def add_comment(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    content = request.form[
        "content"
    ].strip()

    if content:

        comment = Comment(
            content=content,
            user_id=current_user.id,
            post_id=post.id
        )

        db.session.add(comment)
        db.session.commit()

    return redirect(
        url_for(
            "view_post",
            post_id=post.id
        )
    )


# =========================
# Edit Comment - Web
# =========================

@app.route(
    "/comment/<int:comment_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_comment(comment_id):

    comment = Comment.query.get_or_404(
        comment_id
    )

    # Only the comment owner can edit
    if comment.user_id != current_user.id:

        return (
            "You are not allowed to edit this comment.",
            403
        )

    # Update comment
    if request.method == "POST":

        content = request.form[
            "content"
        ].strip()

        if content:

            comment.content = content

            db.session.commit()

            return redirect(
                url_for(
                    "view_post",
                    post_id=comment.post_id
                )
            )

    return render_template(
        "edit_comment.html",
        comment=comment
    )


# =========================
# Delete Comment - Web
# =========================

@app.route(
    "/comment/<int:comment_id>/delete",
    methods=["POST"]
)
@login_required
def delete_comment(comment_id):

    comment = Comment.query.get_or_404(
        comment_id
    )

    # Only the comment owner can delete
    if comment.user_id != current_user.id:

        return (
            "You are not allowed to delete this comment.",
            403
        )

    post_id = comment.post_id

    db.session.delete(comment)
    db.session.commit()

    return redirect(
        url_for(
            "view_post",
            post_id=post_id
        )
    )


# =========================
# Edit Post - Web
# =========================

@app.route(
    "/post/<int:post_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_post(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    # Only post owner can edit
    if post.user_id != current_user.id:

        return (
            "You are not allowed to edit this post.",
            403
        )

    if request.method == "POST":

        post.title = request.form[
            "title"
        ]

        post.content = request.form[
            "content"
        ]

        db.session.commit()

        return redirect(
            url_for(
                "view_post",
                post_id=post.id
            )
        )

    return render_template(
        "edit_post.html",
        post=post
    )


# =========================
# Delete Post - Web
# =========================

@app.route(
    "/post/<int:post_id>/delete",
    methods=["POST"]
)
@login_required
def delete_post(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    # Only post owner can delete
    if post.user_id != current_user.id:

        return (
            "You are not allowed to delete this post.",
            403
        )

    db.session.delete(post)
    db.session.commit()

    return redirect(
        url_for("posts")
    )


# =========================================================
# REST API
# =========================================================


# =========================
# GET All Posts
# =========================

@app.route(
    "/api/posts",
    methods=["GET"]
)
def api_get_posts():

    posts = Post.query.order_by(
        Post.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "created_at":
                post.created_at.isoformat()
                if post.created_at
                else None
        }

        for post in posts
    ])


# =========================
# GET Single Post
# =========================

@app.route(
    "/api/posts/<int:post_id>",
    methods=["GET"]
)
def api_get_post(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    return jsonify({

        "id": post.id,

        "title": post.title,

        "content": post.content,

        "user_id": post.user_id,

        "created_at":
            post.created_at.isoformat()
            if post.created_at
            else None
    })


# =========================
# CREATE Post - REST API
# =========================

@app.route(
    "/api/posts",
    methods=["POST"]
)
def api_create_post():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON data is required"
        }), 400

    title = data.get("title")
    content = data.get("content")
    user_id = data.get("user_id")

    if not title or not content or not user_id:

        return jsonify({
            "error":
                "title, content and user_id are required"
        }), 400

    user = User.query.get(
        user_id
    )

    if not user:

        return jsonify({
            "error": "User not found"
        }), 404

    post = Post(
        title=title,
        content=content,
        user_id=user_id
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({

        "message":
            "Post created successfully",

        "post_id":
            post.id

    }), 201


# =========================
# UPDATE Post - REST API
# =========================

@app.route(
    "/api/posts/<int:post_id>",
    methods=["PUT"]
)
def api_update_post(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    data = request.get_json()

    if not data:

        return jsonify({
            "error":
                "JSON data is required"
        }), 400

    if "title" in data:

        post.title = data["title"]

    if "content" in data:

        post.content = data["content"]

    db.session.commit()

    return jsonify({

        "message":
            "Post updated successfully"

    })


# =========================
# DELETE Post - REST API
# =========================

@app.route(
    "/api/posts/<int:post_id>",
    methods=["DELETE"]
)
def api_delete_post(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    db.session.delete(post)
    db.session.commit()

    return jsonify({

        "message":
            "Post deleted successfully"

    })


# =========================
# GET Comments - REST API
# =========================

@app.route(
    "/api/posts/<int:post_id>/comments",
    methods=["GET"]
)
def api_get_comments(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    comments = Comment.query.filter_by(
        post_id=post.id
    ).order_by(
        Comment.created_at.desc()
    ).all()

    return jsonify([

        {
            "id": comment.id,
            "content": comment.content,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "created_at":
                comment.created_at.isoformat()
                if comment.created_at
                else None
        }

        for comment in comments

    ])


# =========================
# CREATE Comment - REST API
# =========================

@app.route(
    "/api/posts/<int:post_id>/comments",
    methods=["POST"]
)
def api_create_comment(post_id):

    post = Post.query.get_or_404(
        post_id
    )

    data = request.get_json()

    if not data:

        return jsonify({
            "error":
                "JSON data is required"
        }), 400

    content = data.get("content")
    user_id = data.get("user_id")

    if not content or not user_id:

        return jsonify({
            "error":
                "content and user_id are required"
        }), 400

    user = User.query.get(
        user_id
    )

    if not user:

        return jsonify({
            "error":
                "User not found"
        }), 404

    comment = Comment(
        content=content,
        user_id=user_id,
        post_id=post.id
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({

        "message":
            "Comment created successfully",

        "comment_id":
            comment.id

    }), 201


# =========================
# Run Application
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )

