import unicodedata

def is_printable(string):
    """
    A string is printable if it does not contain any unprintable characters.
    Unprintable characters are non-whitespace characters in any Unicode
    'Control' category.
    
    """
    for char in unicode(string):
        try:
            printable = is_printable.cache[char]
        except KeyError:
            is_control = unicodedata.category(char).startswith('C')
            printable = char.isspace() or not is_control
            is_printable.cache[char] = printable
        if not printable:
            return False
    return True
is_printable.cache = {}
