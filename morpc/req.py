import logging

logger = logging.getLogger(__name__)

def get_text_safely(url, headers=None, params=None):
    import requests

    logger.info(f"Getting data from {url} with parameters {params}.")
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        logger.error(f"Request content: {r.url}")
        raise requests.HTTPError
    else:
        logger.debug(f"Request successful. Decoding return JSON.")

        text = r.text

    r.close()

    return text


def get_json_safely(url, headers=None, params=None):
    import requests

    logger.info(f"Getting data from {url} with parameters {params}.")
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        logger.error(f"Request content: {r.url}")
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

def post_safely(url, headers=None, params=None):
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

def delete_safely(url, headers=None, params=None):
    import requests

    logger.info(f"Deleting data at {url} with parameters {params}.")
    r = requests.post(url, headers=headers, params=params)
    if r.status_code != 204:
        logger.error(f"Request content: {r.content}")
        raise requests.HTTPError
    else:
        logger.debug(f"Delete successful.")
    r.close()