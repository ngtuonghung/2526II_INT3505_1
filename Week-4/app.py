from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

authors = {
    1: {"id": 1, "name": "Author One", "birth": 1970, "numOfBooks": 2},
    2: {"id": 2, "name": "Author Two", "birth": 1985, "numOfBooks": 1},
}

books = {
    1: {"id": 1, "title": "Flask Basics", "author": authors[1], "description": "Intro to Flask", "numOfPages": 200, "year": 2020, "cover": {}},
    2: {"id": 2, "title": "Python Deep Dive", "author": authors[1], "description": "Advanced Python", "numOfPages": 350, "year": 2021, "cover": {}},
    3: {"id": 3, "title": "REST API Design", "author": authors[2], "description": "API best practices", "numOfPages": 180, "year": 2022, "cover": {}},
}

next_id = 4


@app.get("/books")
def get_book_list():
    page = request.args.get("page", type=int)
    if page is None:
        return jsonify({"message": "page is required"}), 400

    title_filter = request.args.get("title")
    author_id_filter = request.args.get("author_id", type=int)

    result = list(books.values())
    if title_filter:
        result = [b for b in result if title_filter.lower() in b["title"].lower()]
    if author_id_filter:
        result = [b for b in result if b["author"]["id"] == author_id_filter]

    page_size = 10
    start = (page - 1) * page_size
    return jsonify(result[start:start + page_size]), 200


@app.post("/books")
def create_book():
    global next_id
    data = request.get_json()
    if not data or "title" not in data or "author" not in data:
        return jsonify({"message": "title and author are required"}), 400

    author = authors.get(data["author"])
    if not author:
        return jsonify({"message": "author not found"}), 400

    book = {
        "id": next_id,
        "title": data["title"],
        "author": author,
        "description": data.get("description", ""),
        "numOfPages": data.get("numOfPages", 2),
        "year": data.get("year", 0),
        "cover": {},
    }
    books[next_id] = book
    next_id += 1
    return jsonify(book), 201


@app.get("/books/<int:book_id>")
def get_book(book_id):
    book = books.get(book_id)
    if not book:
        return jsonify({"message": "book not found"}), 404
    return jsonify(book), 200


@app.patch("/books/<int:book_id>")
def update_book(book_id):
    book = books.get(book_id)
    if not book:
        return jsonify({"message": "book not found"}), 404

    data = request.get_json()
    required = {"title", "author_id", "description", "numOfPages", "year", "cover"}
    if not data or not required.issubset(data.keys()):
        return jsonify({"message": "missing required fields"}), 400

    author = authors.get(data["author_id"])
    if not author:
        return jsonify({"message": "author not found"}), 400

    book.update({
        "title": data["title"],
        "author": author,
        "description": data["description"],
        "numOfPages": data["numOfPages"],
        "year": data["year"],
        "cover": data["cover"],
    })
    return jsonify({"data": book}), 200


@app.delete("/books/<int:book_id>")
def delete_book(book_id):
    if book_id not in books:
        return jsonify({"message": "book not found"}), 404
    del books[book_id]
    return jsonify(None), 204


if __name__ == "__main__":
    app.run(debug=True)
