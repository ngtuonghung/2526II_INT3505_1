# BookCreate



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**author** | **int** |  | 
**description** | **str** |  | [optional] 
**num_of_pages** | **int** |  | [optional] 
**year** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.book_create import BookCreate

# TODO update the JSON string below
json = "{}"
# create an instance of BookCreate from a JSON string
book_create_instance = BookCreate.from_json(json)
# print the JSON string representation of the object
print(BookCreate.to_json())

# convert the object into a dict
book_create_dict = book_create_instance.to_dict()
# create an instance of BookCreate from a dict
book_create_from_dict = BookCreate.from_dict(book_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


