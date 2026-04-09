from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import base64
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

BOOKS_SELECT = '''
SELECT b.id, b.title, b.published_year, b.available, b.created_at,
a.name AS author_name, c.name AS category_name
FROM books b
LEFT JOIN authors a ON b.author_id = a.id
LEFT JOIN categories c ON b.category_id = c.id
'''

PAGE_SIZE = 5
PAGE_SIZE_LIMIT = 50

def get_conn():
    return mysql.connector.connect(**DB)

def to_dict(cur, rows):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in rows]

# Encodes a book ID into a base64 cursor token for use in cursor-based pagination
# Input: id (int)
# Output: str (base64-encoded token)
def encode_cursor(id):
    return base64.b64encode(f"cursor:{id}".encode()).decode()

# Decodes a cursor token back to a book ID. Returns None if the token is invalid
# Input: token (str)
# Output: id (int) | None
def decode_cursor(token):
    try:
        decoded = base64.b64decode(token.encode()).decode()
        _, raw_id = decoded.split("cursor:")
        id = int(raw_id)
        if id < 0:
            raise ValueError
        return id
    except Exception:
        return None

# Returns all books with author and category info (no pagination)
# Input: none
# Output: JSON { count, data[] }
@app.get("/book/all")
def book_all():
    conn = get_conn()
    cur = conn.cursor(prepared=True)
    cur.execute(BOOKS_SELECT, ())
    rows = to_dict(cur, cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"count": len(rows), "data": rows})

# Returns a page of books using page-number-based pagination
# Input: query params page (required), page_size (optional, default 5, max 50)
# Output: JSON { count, page, page_size, data[] }
@app.get("/book/page")
def book_page():
    page = request.args.get("page")
    if page is None:
        return jsonify({"error": "missing required param: page"}), 400

    page = max(1, int(page))
    page_size = max(1, min(int(request.args.get("page_size", PAGE_SIZE)), PAGE_SIZE_LIMIT))
    offset = (page - 1) * page_size

    conn = get_conn()
    cur = conn.cursor(prepared=True)
    cur.execute(f"{BOOKS_SELECT} LIMIT %s OFFSET %s", (page_size, offset))
    rows = to_dict(cur, cur.fetchall())
    cur.close()
    conn.close()

    return jsonify({
        "count": len(rows),
        "page": page,
        "page_size": page_size,
        "data": rows,
    })

# Returns a slice of books using raw offset/limit-based pagination
# Input: query params offset (required), limit (required, max 50)
# Output: JSON { count, offset, limit, data[] }
@app.get("/book/offset")
def book_offset():
    offset = request.args.get("offset")
    limit = request.args.get("limit")
    if offset is None or limit is None:
        return jsonify({"error": "missing required params: offset, limit"}), 400

    offset = max(0, int(offset))
    limit = max(1, min(int(limit), PAGE_SIZE_LIMIT))

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
        "data": rows,
    })

# Returns a page of books using cursor-based pagination
# Input: query params continue (optional cursor token), size (optional, default 5, max 50)
# Output: JSON { count, size, next (URL for next page or null), data[] }
@app.get("/book/cursor")
def book_cursor():
    token = request.args.get("continue")
    size = max(1, min(int(request.args.get("size", PAGE_SIZE)), PAGE_SIZE_LIMIT))
    if token is not None:
        after_id = decode_cursor(token)
        if after_id is None:
            return jsonify({"error": "invalid cursor"}), 400
    else:
        after_id = 0

    conn = get_conn()
    cur = conn.cursor(prepared=True)

    cur.execute(
        f"{BOOKS_SELECT} WHERE b.id > %s ORDER BY b.id LIMIT %s",
        (after_id, size),
    )
    rows = to_dict(cur, cur.fetchall())

    cur.close()
    conn.close()

    next_path = None
    if len(rows) > 0:
        next_token = encode_cursor(rows[-1]["id"])
        next_path = f"/book/cursor?continue={next_token}&size={size}"

    return jsonify({
        "count": len(rows),
        "size": size,
        "next": next_path,
        "data": rows,
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)