import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using Http;
using Rest;

@service(#{ title: "book management system", version: "1337" })
@server("https://127.0.0.1:5000/v1", "dev")
@server("https://week-4-nu-two.vercel.app/", "prod")
namespace BookManagement;


/** Creator of books. */
model Author {
  id: int32;
  name: string;
  @minValue(0) birth: int32;
  numOfBooks: int32;
}

model Book {
  id: int32;
  title: string;
  author: Author;
  description: string;
  @minValue(2) numOfPages: int32;
  @minValue(0) year: int32;
  cover: Record<unknown>;
}

model BookCreate {
  title: string;
  /** Author id */
  author: int32;
  description?: string;
  @minValue(2) numOfPages?: int32;
  @minValue(0) year?: int32;
}

/** Data transfer object for partially updating an existing Book (PATCH operation).
    Note: all fields are required to match the original spec. */
model BookPartialUpdate {
  title: string;
  author_id: int32;
  description: string;
  numOfPages: int32;
  year: int32;
  cover: Record<unknown>;
}


@error
model BadRequestError {
  @statusCode statusCode: 400;
  message: string;
}

@error
model NotFoundError {
  @statusCode statusCode: 404;
  message: string;
}

@error
model InternalServerError {
  @statusCode statusCode: 500;
  message: string;
}


model BookCreatedResponse {
  @statusCode statusCode: 201;
  @body book: Book;
}

model UpdateBookOk {
  @statusCode statusCode: 200;
  @body body: {
    data: Book;
  };
}

model DeleteBookNoContent {
  @statusCode statusCode: 204;
}


@route("/books")
@tag("books")
interface Books {
  /** Get book list by pages */
  @get
  @operationId("getBookList")
  list(
    /** Filter by title */
    @query title?: string,

    /** Filter by author id */
    @query author_id?: int32,

    /** Page number */
    @query page: int32,
  ): Book[] | BadRequestError | InternalServerError;

  /** Create new book */
  @post
  @operationId("createBook")
  create(@body body: BookCreate): BookCreatedResponse | BadRequestError;
}


@route("/books/{book_id}")
@tag("books")
interface BookItem {
  /** Get book by id */
  @get
  @operationId("getBook")
  read(
    /** Book id */
    @path book_id: int32,
  ): Book | BadRequestError | NotFoundError | InternalServerError;

  /** Update book info */
  @patch
  @operationId("updateBook")
  update(
    @path book_id: int32,
    @body body: BookPartialUpdate,
  ): UpdateBookOk | BadRequestError | NotFoundError | InternalServerError;

  /** Delete book by id */
  @delete
  @operationId("deleteBook")
  remove(
    @path book_id: int32,
  ): DeleteBookNoContent | BadRequestError | NotFoundError | InternalServerError;
}