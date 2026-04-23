import unittest

from flask import json

from openapi_server.models.product import Product  # noqa: E501
from openapi_server.models.product_input import ProductInput  # noqa: E501
from openapi_server.test import BaseTestCase


class TestProductsController(BaseTestCase):
    """ProductsController integration test stubs"""

    def test_products_get(self):
        """Test case for products_get

        List all products
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/products',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_id_delete(self):
        """Test case for products_id_delete

        Delete a product
        """
        headers = { 
        }
        response = self.client.open(
            '/products/{id}'.format(id='id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_id_get(self):
        """Test case for products_id_get

        Get a product by id
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/products/{id}'.format(id='id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_id_put(self):
        """Test case for products_id_put

        Update a product
        """
        product_input = {"price":0.8008282,"name":"name","description":"description","stock":6}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/products/{id}'.format(id='id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(product_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_post(self):
        """Test case for products_post

        Create a product
        """
        product_input = {"price":0.8008282,"name":"name","description":"description","stock":6}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/products',
            method='POST',
            headers=headers,
            data=json.dumps(product_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
