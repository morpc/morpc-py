import logging
from os import PathLike
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

def get_file_safely(url, output_dir: str | PathLike, chunk_size:int=4096, params=None, headers=default_headers, session: Session | None = None, returnPath: bool = False):
    from requests import Session
    import os

    if not isinstance(session, Session):
        session = Session()

    filename = os.path.basename(url)
    filepath = os.path.join(output_dir, filename)

    logger.debug(f"Getting file from {url} with parameters {params}.")
    with session.get(url, params=params, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(filepath, "wb") as file:
            for chunk in r.iter_content(chunk_size=chunk_size):
                file.write(chunk)

    if returnPath:
        return filepath

def get_private_release_asset(url, output_dir: str | PathLike, token: str, chunk_size: int = 4096, returnPath: bool = False):
    """Download a private repo's GitHub release asset via the authenticated assets API.

    A private repo's release asset URL (the browser_download_url shape get_file_safely() otherwise
    uses) only serves an authenticated browser session -- a bearer token on that same URL still 404s.
    GitHub's assets API endpoint (/repos/{owner}/{repo}/releases/assets/{id}) does accept a token, but
    addresses the asset by its numeric id rather than by this URL, so this first resolves the release
    by tag to find that id, then downloads through the assets API.

    Parameters
    ----------
    url : str
        A release asset URL matching the release_asset_url() shape.
    output_dir : str or PathLike
        The directory to write the downloaded file to.
    token : str
        A GitHub token with access to the private repository.
    chunk_size : int
        Optional. Streaming chunk size in bytes. Defaults to 4096.
    returnPath : bool
        Optional. If True, return the path to the downloaded file. Defaults to False.

    Returns
    -------
    str or None
        The path to the downloaded file, if returnPath is True.
    """
    import os
    import requests
    from morpc.frictionless.release import parse_release_asset_url

    parsed = parse_release_asset_url(url)
    if parsed is None:
        raise ValueError(f"Not a recognized GitHub release asset URL: {url}")
    owner, repo, tag, filename = parsed

    apiHeaders = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    releaseUrl = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    logger.debug(f"Resolving private release asset id for {filename} in {owner}/{repo}@{tag}.")
    r = requests.get(releaseUrl, headers=apiHeaders)
    r.raise_for_status()
    asset = next((a for a in r.json().get("assets", []) if a["name"] == filename), None)
    if asset is None:
        raise RuntimeError(f"Asset {filename} not found in release {tag} of {owner}/{repo}")

    assetHeaders = {"Authorization": f"Bearer {token}", "Accept": "application/octet-stream"}
    filepath = os.path.join(output_dir, filename)
    logger.debug(f"Downloading private release asset from {asset['url']} to {filepath}.")
    with requests.get(asset["url"], headers=assetHeaders, stream=True) as resp:
        resp.raise_for_status()
        with open(filepath, "wb") as file:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                file.write(chunk)

    if returnPath:
        return filepath


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