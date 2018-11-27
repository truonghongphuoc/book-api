from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
POSTGRES = {
    'user': os.environ['DATABASE_USER'],
    'pw': os.environ['DATABASE_PASSWORD'],
    'db': os.environ['DATABASE_NAME'],
    'host': os.environ['DATABASE_HOST'],
    'port': os.environ['DATABASE_PORT']
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://book:123456789a@@localhost/books'

db = SQLAlchemy(app)


class Books(db.Model):
    __tableName__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(80))
    author = db.Column(db.String(120))

    def __init__(self, book_name, author):
        self.book_name = book_name
        self.author = author

    def __repr__(self):
        return '<Book %r>' % self.book_name


@app.route('/')
def index():
    return 'OK'


@app.route('/books', methods=['POST', 'GET', 'OPTIONS'])
def book():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    elif request.method == 'GET':
        books_data = Books.query.all()
        json_list = []
        if books_data:
            for b in books_data:
                item = {
                    "id": b.id,
                    "book_name": b.book_name,
                    "author": b.author
                }
                json_list.append(item)
        return make_response(_corsify_actual_response(jsonify(json_list)))

    elif request.method == 'POST':
        data = request.get_json()
        new_book = Books(data['book_name'], data['author'])
        db.session.add(new_book)
        db.session.commit()
        return _corsify_actual_response(jsonify({"success": True}))


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
