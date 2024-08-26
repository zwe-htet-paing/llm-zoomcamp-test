import requests
import json
import io
import docx
from typing import List, Dict

from mage_ai.shared.hash import dig
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():q
    from mage_ai.data_preparation.decorators import test


@data_loader
def ingest_api_data(*args, **kwargs) -> List[Dict]:
    """
    Template for loading data from an API.
    Fetch data from external API using the provided configurations.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        endpoint (str): API endpoint URL.
        auth_token (str): Authentication token for the API.
        method (str): HTTP method to use (GET, POST, etc.).
        timeout (int): Request timeout in seconds.
    """
    endpoint = kwargs.get('endpoint')
    auth_token = kwargs.get('auth_token')
    method = kwargs.get('method', 'GET')
    timeout = kwargs.get('timeout', 30)
    parser = kwargs.get('parser')

    headers = {}
    if auth_token:
        headers['Authorization'] = f"Bearer {auth_token}"

    response = requests.request(
        method=method,
        url=endpoint or  '',
        headers=headers,
        timeout=timeout
    )
    response.raise_for_status()
    with io.BytesIO(response.content) as f_in:
        doc = docx.Document(f_in)
    questions = []
    question_heading_style = 'heading 2'
    section_heading_style = 'heading 1'
    
    heading_id = ''
    section_title = ''
    question_title = ''
    answer_text_so_far = ''
    for p in doc.paragraphs:
        style = p.style.name.lower()
        p_text = clean_line(p.text)
    
        if len(p_text) == 0:
            continue
    
        if style == section_heading_style:
            section_title = p_text
            continue
    
        if style == question_heading_style:
            answer_text_so_far = answer_text_so_far.strip()
            if answer_text_so_far != '' and section_title != '' and question_title != '':
                questions.append({
                    'text': answer_text_so_far,
                    'section': section_title,
                    'question': question_title,
                })
                answer_text_so_far = ''
    
            question_title = p_text
            continue
        
        answer_text_so_far += '\n' + p_text
    
    answer_text_so_far = answer_text_so_far.strip()
    if answer_text_so_far != '' and section_title != '' and question_title != '':
        questions.append({
            'text': answer_text_so_far,
            'section': section_title,
            'question': question_title,
        })

    return questions


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'