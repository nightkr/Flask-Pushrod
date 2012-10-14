from flask import Flask
from flask.ext.pushrod import Pushrod, pushrod_view
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.sql.functions import now

app = Flask(__name__)
Pushrod(app)
db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=now())
    title = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey(Author.id), nullable=False)
    author = db.relationship(Author, backref='posts')


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=now())
    content = db.Column(db.Text, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey(Post.id), nullable=False)
    post = db.relationship(Post, backref='comments')


@app.route("/")
@app.route("/<int:page>")
@pushrod_view()
def list_posts(page=1):
    posts = Post.query.paginate(page)

    return {
        'page': page,
        'pages': posts.pages,
        'total': posts.total,
        'items': [{
            'id': post.id,
            'title': post.title,
            'timestamp': unicode(post.timestamp),
            'content': post.content,
            'author': {
                'name': post.author.name,
                'description': post.author.description,
            },
        } for post in posts.items]
    }


@app.route("/posts/<int:id>")
@pushrod_view()
def blog_post(id):
    post = Post.query.get_or_404(id)

    return {
        'item': {
            'id': post.id,
            'title': post.title,
            'timestamp': unicode(post.timestamp),
            'content': post.content,

            'author': {
                'name': post.author.name,
                'description': post.author.description,
            },

            'comments': [{
                'author': comment.author,
                'timestamp': unicode(comment.timestamp),
                'content': comment.content,
            } for comment in post.comments]
        }
    }


if __name__ == '__main__':  # pragma: no cover
    app.run()
