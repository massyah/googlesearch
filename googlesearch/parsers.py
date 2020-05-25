from dataclasses import field, dataclass
from datetime import datetime
from typing import List
from urllib.parse import parse_qs, urlparse

import dateparser
from bs4 import BeautifulSoup
from loguru import logger


@dataclass
class GoogleResult(object):
    """Represents a google search result."""
    name: str = None
    link: str = None
    description: str = None
    updated_at: datetime = None
    rank: str = None
    breadcrumb: str = None

    def set_updated_at_from_str(self, s):
        if s is not None:
            self.updated_at = dateparser.parse(s)


@dataclass
class GoogleSearch(object):
    related_searches: List[str] = field(default_factory=list)
    results: List[GoogleResult] = field(default_factory=list)

    @classmethod
    def from_html(cls, html):
        this_res = GoogleSearch()
        soup = BeautifulSoup(html, "html.parser")
        divs = soup.findAll("div", attrs={"class": "ezO2md"})
        this_res.related_searches = [x.text for x in soup.findAll("a", attrs={"class": "ZWRArf"})]

        for j, li in enumerate(divs):
            res = GoogleResult()
            res.rank = j
            res.name = _get_name(li)
            res.link = _get_link(li)
            res.breadcrumb, res.description, d = _get_bcrumbs_uat_description(li)
            res.set_updated_at_from_str(d)
            this_res.results.append(res)

        logger.info("Yielding {} results", len(this_res.results))

        return this_res


def _filter_link(link):
    '''Filter links found in the Google result pages HTML code.
    Returns None if the link doesn't yield a valid result.
    '''
    try:
        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urlparse(link, 'http')
        # link type-1
        # >>> "https://www.gitbook.com/book/ljalphabeta/python-"
        if o.netloc and 'google' not in o.netloc:
            return link
        # link type-2
        # >>> "http://www.google.com/url?url=http://python.jobbole.com/84108/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggUMAA&usg=AFQjCNHPws5Buru5Z71wooRLHT6mpvnZlA"
        if o.netloc and o.path.startswith('/url'):
            try:
                link = parse_qs(o.query)['url'][0]
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link
            except KeyError:
                pass
        # Decode hidden URLs.
        if link.startswith('/url?'):
            try:
                # link type-3
                # >>> "/url?q=http://python.jobbole.com/84108/&sa=U&ved=0ahUKEwjFw6Txg4_UAhVI5IMKHfqVAykQFggUMAA&usg=AFQjCNFOTLpmpfqctpIn0sAfaj5U5gAU9A"
                link = parse_qs(o.query)['q'][0]
                # Valid results are absolute URLs not pointing to a Google domain
                # like images.google.com or googleusercontent.com
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link
            except KeyError:
                # link type-4
                # >>> "/url?url=https://machine-learning-python.kspax.io/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggfMAI&usg=AFQjCNEfkUI0RP_RlwD3eI22rSfqbYM_nA"
                link = parse_qs(o.query)['url'][0]
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
    return None


def _get_link(li):
    """Return external link from a search."""
    try:
        a = li.find("a")
        link = a["href"]
    except Exception:
        return None
    return _filter_link(link)


# PRIVATE
def _get_name(li):
    """Return the name of a google search."""
    try:
        return li.find('span', attrs={"class": 'qXLe6d'}).text.strip()
    except Exception as e:
        return None


def _get_bcrumbs_uat_description(li):
    """Return the description of a google search.
    TODO: There are some text encoding problems to resolve."""
    bcrumbs, description, updated_at = None, None, None
    topdiv = li.findAll("span", attrs={"class": "fYyStc"})
    bcrumbs = "".join([x.text for x in topdiv if " › " in x.text]).strip()
    sdiv = li.find("div", attrs={"class": "YgS6de"})
    if sdiv:
        stspan = sdiv.findAll("span", attrs={"class": "fYyStc"})
        description = "".join([x.text for x in stspan if "YVIcad" not in x.attrs.get('class', [])]).strip()
        updated_at = "".join([x.text for x in stspan if "YVIcad" in x.attrs.get('class', [])]).strip()
        description = description.replace(u'\xa0', u' ').replace("\n", " ").strip()
    return bcrumbs, description, updated_at
