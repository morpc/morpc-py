import logging
from time import sleep
from httpx import head
from pydantic import FilePath
from requests import HTTPError, Session

logger = logging.getLogger(__name__)

default_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}


def get_text_safely(url, params=None, headers=default_headers, session: Session | None = None):
    import requests

    if not isinstance(session, Session):
        session = Session()

    logger.debug(f"Getting data from {url} with parameters {params}.")
    r = session.get(url, headers=headers, params=params)
    if r.status_code != 200:
        logger.error(f"Request content: {r.url}")
        raise requests.HTTPError
    else:
        logger.debug(f"Request successful. Returning plain text.")

        text = r.text


    return text


def get_json_safely(url, params=None, headers=default_headers, session: Session | None = None, returnurl: bool = False):
    import requests

    if not isinstance(session, Session):
        session = Session()

    logger.debug(f"Getting data from {url} with parameters {params}.")
    r = session.get(url, params=params, headers=headers)
    if r.status_code != 200:
        if "Output format not supported" in r.text:
            logger.error(f"Output format not supported: {params['f']}")
            raise HTTPError(f"Output format not supported: {params['f']}")
        if r.status_code == 500:
            logger.error(f"Status Code 500: retrying request")
            r = session.get(url, params=params, headers=headers)
            if r.status_code != 200:
                logger.error(f"Failed second attempt, aborting.")
                raise HTTPError
            else:
                json = r.json()
        else:
            logger.error(f"Request failed. Content: {r.content}")
    else:
        logger.debug(f"Request successful. Decoding return JSON.")
        try:
            json = r.json()
            if 'error' in json:
                if json['error']['code'] == 500:
                    sleep(1)
                    try:
                        r=session.get(url=url, params=params, headers=headers)
                        json = r.json()
                    except Exception as e:
                        logger.error(f"Request failed: {r.url}")
                        logger.error(f"Failed second attempt. {e}")
                        raise RuntimeError
                logger.error(f"Server returned error {json['error']}")
        except:
            logger.error(f"JSONDecoderError. Check the url. {r.url}")
            raise requests.JSONDecodeError

    if returnurl:
        return json, r.url
    else:
        return json

def post_safely(url, params=None, headers=None):
    import requests

    logger.info(f"Posting data to {url} with parameters {params}.")
    r = requests.post(url, headers=headers, params=params)
    if r.status_code != 201:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError
    else:
        logger.debug(f"Request successful. Decoding return JSON.")
        try:
            json = r.json()
        except:
            logger.error(f"JSONDecoderError. Check the url. {r.url}")
            raise requests.JSONDecodeError
    r.close()

    return json

def delete_safely(url, params=None, headers=None):
    import requests

    logger.info(f"Deleting data at {url} with parameters {params}.")
    r = requests.post(url, headers=headers, params=params)
    if r.status_code != 204:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError
    else:
        logger.debug(f"Delete successful.")
    r.close()

def get_file(url, archive_dir = './input_data', filename = None, return_filepath=False, headers=default_headers, chunk_size=1024):
    
    import requests
    import os

    r = requests.get(url, headers=headers, stream=True)
    path = os.path.join(archive_dir, filename)
    with open(path, 'wb') as file:
        for chunk in r.iter_content(chunk_size=chunk_size):
            file.write(chunk)
    
    if return_filepath:
        return path