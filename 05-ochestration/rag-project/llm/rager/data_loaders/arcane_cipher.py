from typing import Dict, List, Union

import numpy as np
from elasticsearch import Elasticsearch, exceptions

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

SAMPLE_QUESTION = "When is the next cohort?"


@data_loader
def search(*args, **kwargs) -> List[Dict]:
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    index_name = kwargs.get('index_name', 'documents_20240818_4321')
    top_k = kwargs.get('top_k', 5)

    question = ''
    if len(args):
        question = args[0]
    if not question:
        question = SAMPLE_QUESTION

    query = {
        "bool": {
            "must": {
                "multi_match": {
                    "query": question,
                    "fields": ["question^3", "text"],
                    "type": "best_fields"
                }
            },
        }
    }


    es_client = Elasticsearch(connection_string)

    try:
        response = es_client.search(
            index=index_name,
            body={
                "size": top_k,
                "query": query,
            },
        )

        top_match = response['hits']['hits'][0]['_source']['document_id']
        print(top_match)
        return top_match
    
    except exceptions.BadRequestError as e:
        print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'