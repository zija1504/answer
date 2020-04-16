from answer.scraper import parse_links, _parse_content, _parse_to_text


def test_parse_links():
    """Test parser function."""
    with open("tests/link.html") as file_google:
        string = file_google.read()
        links = parse_links(string)
        assert links
        links = parse_links(string, 3)
        assert len(links) == 3


def test_scrapper():
    with open("tests/file.html") as file_stack:
        string = file_stack.read()
        query = {
            "code": False,
            "color": True
        }
        answer = _parse_to_text(string, query)
        assert False
