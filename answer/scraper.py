# -*- coding: utf-8 -*-

"""A parser module.

Notice the comment above the docstring specifying the encoding.
Docstrings do appear in the bytecode, so you can access this through
the ``__doc__`` attribute. This is also what you'll see if you call
help() on a module or any other Python object.
"""
import asyncio
import logging
import os
import re
from typing import List, Match, Optional, Tuple

from lxml import html as lhtml
from lxml.html import HtmlElement
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

SITE = os.getenv("SITE", "https://stackoverflow.com/questions/")
MAX = int(os.getenv("MAX", 10))


def _is_question(links: List[str], max_n: int) -> List[str]:
    question_links = []
    for link in links:
        match: Optional[Match[str]] = re.search(r'questions/(\d+/)', link)
        if match:
            question_links.append(SITE + match.group(1))
    return question_links


def _parse_links(text: str, max_n: int) -> List[str]:
    logger.debug('getting post links')
    html: HtmlElement = lhtml.fromstring(text)
    links: List[HtmlElement] = html.cssselect('a')
    links = [el.get('href') for el in links]
    return _is_question(links, max_n)


def parse_links(text: str, max_n: int = MAX) -> List[str]:
    """Parsing html site in order to find links.

    Parameters
    ----------
        text : str
            text in html format to parse
        max_n : int, optional
            max number of returned list, default from env or 10,
            other from command line args, by default MAX

    Returns
    -------
        List[str]
            list of  href links to stackoverflow questions(default)
    """
    return _parse_links(text, max_n)


def _parse_content(
    text: str, number_of_answers: int = 0,
) -> Tuple[List[str], HtmlElement]:
    logger.debug('getting anwser')
    html: HtmlElement = lhtml.fromstring(text)
    try:
        tags = html.cssselect('a.post-tag')
        tags = [elem.text_content() for elem in tags]
    except Exception as err:
        tags = []
        logger.error(err)
    answercell: HtmlElement = html.cssselect(
        'div.answercell > div.post-text',
    )[number_of_answers]
    return tags, answercell


def _format_output(code: str, tags: List[str], args):
    # TODO: stolen from howdoi, should write my version
    if not args['color']:
        logger.debug("color")
        return code
    lexer = None
    for keyword in tags:
        try:
            lexer = get_lexer_by_name(keyword)
            break
        except ClassNotFound as err:
            logger.debug(err)

    # no lexer found above, use the guesser
    if not lexer:
        try:
            lexer = guess_lexer(code)
        except ClassNotFound as err1:
            logger.debug(f'{err1}\nNo lexer guessed')
            return code
    return highlight(code, lexer, TerminalFormatter(bg='dark'))


def _parse_to_text(text: str, args):
    tags, answer = _parse_content(text)
    if not args['all']:
        answer = answer.cssselect('pre')
        code = '\n'.join(elem.text_content() for elem in answer)
        return _format_output(code, tags, args)

    texts = []
    for elem_to_drop in answer.iter(["span", "br", "code"]):
        elem_to_drop.drop_tag()
    for elem in answer.iter():
        elem_text: str = elem.text
        if elem_text:
            if elem.tag == 'pre':
                texts.append(_format_output(elem_text, tags, args))
            else:
                re_elem_text = re.sub(r'\s\s+', ' ', elem_text)
                texts.append(re_elem_text + '\n')
    return '\n'.join(texts)


def parse_to_text(text: str, args) -> str:
    """Get first and best anwser for your question.

    From source code of site with question scrap most
    voted answer. If add parameter -c --code to comannd line
    only code from answer will be printed out

    Args:
        text (str): source code of site
        args (Dict[str, Any]): Dictionary from command line

    Returns:
        str: return answer
    """
    return _parse_to_text(text, args)
