"""Data preparation functions."""


def flatten_list(data):
    """
    Flattens a list of dictionaries and lists of dictionaries into a flat list of dictionaries.
    """
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(item)
        elif isinstance(item, list):
            result.extend(flatten_list(item))
    return result
