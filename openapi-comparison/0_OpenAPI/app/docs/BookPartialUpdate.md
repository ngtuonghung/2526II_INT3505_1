# BookPartialUpdate

Data transfer object for partially updating an existing Book (PATCH operation).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**author_id** | **int** |  | 
**description** | **str** |  | 
**num_of_pages** | **int** |  | 
**year** | **int** |  | 
**cover** | **object** |  | 

## Example

```python
from openapi_client.models.book_partial_update import BookPartialUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of BookPartialUpdate from a JSON string
book_partial_update_instance = BookPartialUpdate.from_json(json)
# print the JSON string representation of the object
print(BookPartialUpdate.to_json())

# convert the object into a dict
book_partial_update_dict = book_partial_update_instance.to_dict()
# create an instance of BookPartialUpdate from a dict
book_partial_update_from_dict = BookPartialUpdate.from_dict(book_partial_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


