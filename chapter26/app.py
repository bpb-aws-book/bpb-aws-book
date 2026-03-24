import json

BOOKS = [
    {"id": 1, "name": "Clean Code: A Handbook of Agile Software Craftsmanship", "description": "My fav book", "author": "Robert C Martin", "price": 35.99, "is_rented": False},
    {"id": 2, "name": "Code Complete: A Practical Handbook of Software Construction", "description": "One of the best practical guides to programming", "author": "Steve McConnell", "price": 54.99, "is_rented": False},
    {"id": 3, "name": "Head First Software Architecture: A Learners Guide to Architectural Thinking", "description": "Teaches software architecture", "author": "Raju Gandhi", "price": 505.99, "is_rented": False},
    {"id": 4, "name": "The Warren Buffett Way", "description": "An insightful new take on the life and work of one of the worlds most remarkable investors", "author": "Robert G. Hagstrom", "price": 54.99, "is_rented": False},
]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def get_root(event, context):
    return _response(200, {
        "message": "Books Search API",
        "endpoints": [
            {"method": "GET", "path": "/books", "description": "List all books"},
            {"method": "GET", "path": "/books/{bookId}", "description": "Get a book by ID (1-4)"},
        ],
    })


def list_books(event, context):
    return _response(200, BOOKS)


def get_book(event, context):
    book_id_str = event.get("pathParameters", {}).get("bookId")
    if not book_id_str:
        return _response(400, {"error": "Missing bookId path parameter"})

    try:
        book_id = int(book_id_str)
    except ValueError:
        return _response(400, {"error": "bookId must be an integer"})

    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return _response(404, {"error": f"Book with id {book_id} not found"})

    return _response(200, book)
