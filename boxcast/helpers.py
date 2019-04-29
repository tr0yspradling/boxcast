from urllib.parse import unquote, urlencode, urlparse, parse_qs


def __prep_pagination_args(page_number=0, limit_size=50, sort_order=''):
    return '?p={0}&s={1}&l={2}'.format(page_number, sort_order, limit_size)


def merge_url_query_params(url: str, additional_params: dict) -> str:
    url_components = urlparse(url)
    original_params = parse_qs(url_components.query)
    # Before Python 3.5 you could update original_params with
    # additional_params, but here all the variables are immutable.
    merged_params = {**original_params, **additional_params}
    updated_query = urlencode(merged_params, doseq=True)
    # _replace() is how you can create a new NamedTuple with a changed field
    return url_components._replace(query=updated_query).geturl()


args = {
    'q': 'timeframe:current timeframe:future'
}

url = 'https://api.boxcast.com/broadcasts' + __prep_pagination_args()
x = merge_url_query_params(url, args)
