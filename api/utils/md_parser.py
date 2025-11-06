import re


def parse_markdown_headers(markdown):
    headers = re.findall(r'#{1,6} (.+)', markdown)
    return headers


def parse_markdown_list(markdown):
    items = re.findall(r'-\s+(.+)', markdown)
    return items
