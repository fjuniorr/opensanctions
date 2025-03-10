import warnings
from typing import Any, Optional
from functools import partial
from pathlib import Path
from requests import Session
from urllib3.exceptions import InsecureRequestWarning

from zavod import settings
from zavod.logs import get_logger

log = get_logger(__name__)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


def make_session(user_agent: str = settings.HTTP_USER_AGENT) -> Session:
    session = Session()
    session.headers["User-Agent"] = user_agent
    session.verify = False
    session.request = partial(  # type: ignore
        session.request,
        timeout=settings.HTTP_TIMEOUT,
    )
    return session


def fetch_file(
    session: Session,
    url: str,
    name: str,
    data_path: Path = settings.DATA_PATH,
    auth: Optional[Any] = None,
    headers: Optional[Any] = None,
) -> Path:
    """Fetch a (large) file via HTTP to the data path."""
    out_path = data_path.joinpath(name)
    if out_path.exists():
        return out_path
    log.info("Fetching file", url=url)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with session.get(url, auth=auth, headers=headers, stream=True) as res:
        res.raise_for_status()
        with open(out_path, "wb") as fh:
            for chunk in res.iter_content(chunk_size=8192 * 10):
                fh.write(chunk)
    return out_path
