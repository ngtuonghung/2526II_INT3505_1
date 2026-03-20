# Book



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**title** | **str** |  | 
**author** | [**Author**](Author.md) |  | 
**description** | **str** |  | 
**num_of_pages** | **int** |  | 
**year** | **int** |  | 
**cover** | **object** |  | 

## Example

```python
from openapi_client.models.book import Book

# TODO update the JSON string below
json = "{}"
# create an instance of Book from a JSON string
book_instance = Book.from_json(json)
# print the JSON string representation of the object
print(Book.to_json())

# convert the object into a dict
book_dict = book_instance.to_dict()
# create an instance of Book from a dict
book_from_dict = Book.from_dict(book_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


