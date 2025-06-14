from parser.apache_parser import ApacheParser

def test_apache_parser_valid_line():
    parser = ApacheParser()
    line = '127.0.0.1 - - [10/Jun/2025:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326'
    result = parser.parse(line)
    assert result is not None
    assert result["status"] == 200
    assert result["method"] == "GET"

def test_apache_parser_invalid_line():
    parser = ApacheParser()
    line = "invalid log format"
    result = parser.parse(line)
    assert result is None

