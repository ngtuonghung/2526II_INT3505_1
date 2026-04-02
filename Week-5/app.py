from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

DB = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)

BOOKS_SELECT = (
    "SELECT b.id, b.title, b.published_year, b.available, b.created_at, "
    "a.name AS author_name, c.name AS category_name "
    "FROM books b "
    "LEFT JOIN authors a ON b.author_id = a.id "
    "LEFT JOIN categories c ON b.category_id = c.id"
)


CURSOR_PAGE_SIZE = 5

def get_conn():
    return mysql.connector.connect(**DB)

def to_dict(cur, rows):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in rows]


@app.get("/book/all")
def book_all():
    conn = get_conn()
    cur = conn.cursor(prepared=True)
    cur.execute(BOOKS_SELECT, ())
    rows = to_dict(cur, cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"count": len(rows), "data": rows})


@app.get("/book/page")
def book_page():
    page = request.args.get("page")
    size = request.args.get("size")
    if page is None or size is None:
        return jsonify({"error": "missing required params: page, size"}), 400

    page = max(1, int(page))
    size = max(1, int(size))
    offset = (page - 1) * size

    conn = get_conn()
    cur = conn.cursor(prepared=True)
    cur.execute(f"{BOOKS_SELECT} LIMIT %s OFFSET %s", (size, offset))
    rows = to_dict(cur, cur.fetchall())
    cur.close()
    conn.close()

    return jsonify({
        "count": len(rows),
        "page": page,
        "size": size,
        "next": page + 1 if len(rows) == size else None,
        "previous": page - 1 if page > 1 else None,
        "data": rows,
    })


@app.get("/book/offset")
def book_offset():
    offset = request.args.get("offset")
    limit = request.args.get("limit")
    if offset is None or limit is None:
        return jsonify({"error": "missing required params: offset, limit"}), 400

    offset = max(0, int(offset))
    limit = max(1, int(limit))

    conn = get_conn()
    cur = conn.cursor(prepared=True)
    cur.execute(f"{BOOKS_SELECT} LIMIT %s OFFSET %s", (limit, offset))
    rows = to_dict(cur, cur.fetchall())
    cur.close()
    conn.close()

    return jsonify({
        "count": len(rows),
        "offset": offset,
        "limit": limit,
        "next_offset": offset + limit if len(rows) == limit else None,
        "previous_offset": offset - limit if offset - limit >= 0 else None,
        "data": rows,
    })


@app.get("/book/cursor")
def book_cursor():
    after_id = int(request.args.get("continue", 0))

    conn = get_conn()
    cur = conn.cursor(prepared=True)

    cur.execute(
        f"{BOOKS_SELECT} WHERE b.id > %s ORDER BY b.id LIMIT %s",
        (after_id, CURSOR_PAGE_SIZE),
    )
    rows = to_dict(cur, cur.fetchall())

    cur.close()
    conn.close()

    next_id = rows[-1]["id"] if len(rows) == CURSOR_PAGE_SIZE else None

    return jsonify({
        "size": CURSOR_PAGE_SIZE,
        "next": next_id,
        "data": rows,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
