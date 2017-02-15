def find_json_objects(s):
    """
    Find json objects in a string and returns a list of tuples containing start and
    end locations of json objects in the string `s`
    """
    objects = []
    opens = 0
    start = s.find('{')
    offset = start

    if start < 0: return []

    for index, c in enumerate(s[offset:]):
        if c == '{':
            opens += 1
        elif c == '}':
            opens -= 1
            if opens == 0:
                objects.append((start, index + offset + 1))
                start = index + offset + 1
    return objects
