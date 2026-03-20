# openapi_client.BooksApi

All URIs are relative to *https://127.0.0.1:5000/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_book**](BooksApi.md#create_book) | **POST** /books | Create book
[**delete_book**](BooksApi.md#delete_book) | **DELETE** /books/{book_id} | Delete book
[**get_book**](BooksApi.md#get_book) | **GET** /books/{book_id} | Get book
[**get_book_list**](BooksApi.md#get_book_list) | **GET** /books | Get book list
[**update_book**](BooksApi.md#update_book) | **PATCH** /books/{book_id} | Update book


# **create_book**
> Book create_book(book_create)

Create book

Create new book

### Example


```python
import openapi_client
from openapi_client.models.book import Book
from openapi_client.models.book_create import BookCreate
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://127.0.0.1:5000/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://127.0.0.1:5000/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BooksApi(api_client)
    book_create = openapi_client.BookCreate() # BookCreate | Details of the book to be created.

    try:
        # Create book
        api_response = api_instance.create_book(book_create)
        print("The response of BooksApi->create_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->create_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_create** | [**BookCreate**](BookCreate.md)| Details of the book to be created. | 

### Return type

[**Book**](Book.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Book create successfully |  -  |
**400** | The server could not understand the request due to invalid syntax. The client should modify the request and try again. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_book**
> delete_book(book_id)

Delete book

Delete book by id

### Example


```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://127.0.0.1:5000/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://127.0.0.1:5000/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BooksApi(api_client)
    book_id = 56 # int | Path parameter to retrieve books by.

    try:
        # Delete book
        api_instance.delete_book(book_id)
    except Exception as e:
        print("Exception when calling BooksApi->delete_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**| Path parameter to retrieve books by. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | The request was successful, but there is no content to return in the response. |  -  |
**400** | The server could not understand the request due to invalid syntax. The client should modify the request and try again. |  -  |
**404** | The server cannot find the requested resource. The endpoint may be invalid or the resource may no longer exist. |  -  |
**500** | The server encountered an unexpected condition that prevented it from fulfilling the request. Report the issue to the support team if it persists. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_book**
> Book get_book(book_id)

Get book

Get book by id


### Example


```python
import openapi_client
from openapi_client.models.book import Book
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://127.0.0.1:5000/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://127.0.0.1:5000/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BooksApi(api_client)
    book_id = 56 # int | Path parameter to retrieve books by.

    try:
        # Get book
        api_response = api_instance.get_book(book_id)
        print("The response of BooksApi->get_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->get_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**| Path parameter to retrieve books by. | 

### Return type

[**Book**](Book.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A JSON object containing the book details. |  -  |
**400** | The server could not understand the request due to invalid syntax. The client should modify the request and try again. |  -  |
**404** | The server cannot find the requested resource. The endpoint may be invalid or the resource may no longer exist. |  -  |
**500** | The server encountered an unexpected condition that prevented it from fulfilling the request. Report the issue to the support team if it persists. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_book_list**
> List[Book] get_book_list(page, title=title, author_id=author_id)

Get book list

Get book list by pages

### Example


```python
import openapi_client
from openapi_client.models.book import Book
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://127.0.0.1:5000/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://127.0.0.1:5000/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BooksApi(api_client)
    page = 56 # int | page
    title = 'title_example' # str | To filter book by title (optional)
    author_id = 56 # int | To filter book by author id (optional)

    try:
        # Get book list
        api_response = api_instance.get_book_list(page, title=title, author_id=author_id)
        print("The response of BooksApi->get_book_list:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->get_book_list: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| page | 
 **title** | **str**| To filter book by title | [optional] 
 **author_id** | **int**| To filter book by author id | [optional] 

### Return type

[**List[Book]**](Book.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A JSON array containing book objects. |  -  |
**400** | The server could not understand the request due to invalid syntax. The client should modify the request and try again. |  -  |
**500** | The server encountered an unexpected condition that prevented it from fulfilling the request. Report the issue to the support team if it persists. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_book**
> UpdateBookOk update_book(book_id, book_partial_update)

Update book

Update book info

### Example


```python
import openapi_client
from openapi_client.models.book_partial_update import BookPartialUpdate
from openapi_client.models.update_book_ok import UpdateBookOk
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://127.0.0.1:5000/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://127.0.0.1:5000/v1"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BooksApi(api_client)
    book_id = 56 # int | Path parameter to retrieve books by.
    book_partial_update = openapi_client.BookPartialUpdate() # BookPartialUpdate | 

    try:
        # Update book
        api_response = api_instance.update_book(book_id, book_partial_update)
        print("The response of BooksApi->update_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->update_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**| Path parameter to retrieve books by. | 
 **book_partial_update** | [**BookPartialUpdate**](BookPartialUpdate.md)|  | 

### Return type

[**UpdateBookOk**](UpdateBookOk.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The request was successful, and the server has returned the requested resource in the response body. |  -  |
**400** | The server could not understand the request due to invalid syntax. The client should modify the request and try again. |  -  |
**404** | The server cannot find the requested resource. The endpoint may be invalid or the resource may no longer exist. |  -  |
**500** | The server encountered an unexpected condition that prevented it from fulfilling the request. Report the issue to the support team if it persists. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

