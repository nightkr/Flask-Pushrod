import sys

from datetime import datetime

now = datetime.now()


def setup_db(module):
    module.app.config['SQLALCHEMY_DATABASE_URI'] = \
        "sqlite:///./pushrodr.db"
    module.db.drop_all()
    module.db.create_all()

    with module.app.test_request_context():
        author_one = module.Author()
        author_one.name = "Author One"
        author_one.description = "Spam"
        module.db.session.add(author_one)

        author_two = module.Author()
        author_two.name = "Author Two"
        author_two.description = "Eggs"
        module.db.session.add(author_two)

        post_one = module.Post()
        post_one.id = 1
        post_one.timestamp = now
        post_one.title = "Hello, World!"
        post_one.content = "This is the first post"
        post_one.author = author_one
        module.db.session.add(post_one)

        post_two = module.Post()
        post_two.id = 2
        post_two.timestamp = now
        post_two.title = "Another Test!"
        post_two.content = "This is the second post"
        post_two.author = author_one
        module.db.session.add(post_two)

        post_three = module.Post()
        post_three.id = 3
        post_three.timestamp = now
        post_three.title = "Goodbye, World!"
        post_three.content = "This is the third post"
        post_three.author = author_two
        module.db.session.add(post_three)

        post_two_comment_one = module.Comment()
        post_two_comment_one.post = post_two
        post_two_comment_one.timestamp = now
        post_two_comment_one.author = "Anonymous Coward"
        post_two_comment_one.content = "THIS POST IS TERRIBLE"

        post_two_comment_two = module.Comment()
        post_two_comment_two.post = post_two
        post_two_comment_two.timestamp = now
        post_two_comment_two.author = "AAA"
        post_two_comment_two.content = "BBB"

        post_three_comment_one = module.Comment()
        post_three_comment_one.post = post_three
        post_three_comment_one.timestamp = now
        post_three_comment_one.author = "CCC"
        post_three_comment_one.content = "ASD"

        module.db.session.commit()


if __name__ == '__main__':  # pragma: no cover
    module = __import__(sys.argv[1])
    setup_db(module)
    module.app.run(debug=True)
