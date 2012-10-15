from flask import Flask, g
from flask.ext.pushrod import Pushrod, pushrod_view
from flask.ext.sqlalchemy import SQLAlchemy, Pagination

from sqlalchemy.sql.functions import now

app = Flask(__name__)
pushrod = Pushrod(app)
db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = "authors"
    __pushrod_fields__ = ("name", "description")

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

    def __pushrod_fields__(self):
        fields = ["id", "timestamp", "title", "content", "author"]

        if not getattr(g, 'list_view', False):
            fields.append("comments")

        return fields


class Comment(db.Model):
    __tablename__ = "comments"
    __pushrod_fields__ = ("author", "timestamp", "content")

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=now())
    content = db.Column(db.Text, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey(Post.id), nullable=False)
    post = db.relationship(Post, backref='comments')


def normalize_pagination(x, pushrod):
    return pushrod.normalize({
        'page': x.page,
        'pages': x.pages,
        'total': x.total,
        'items': x.items,
    })

pushrod.normalizers[Pagination] = normalize_pagination


@app.route("/")
@app.route("/<int:page>")
@pushrod_view()
def list_posts(page=1):
    g.list_view = True
    return Post.query.paginate(page)


@app.route("/posts/<int:id>")
@pushrod_view()
def blog_post(id):
    post = Post.query.get_or_404(id)
    return {'item': post}


if __name__ == '__main__':  # pragma: no cover
    app.run()
