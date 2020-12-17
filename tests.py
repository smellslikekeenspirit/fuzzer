import mechanicalsoup

browser = mechanicalsoup.StatefulBrowser()

"""
Checks if data passed to an HTTP request was sanitized before output.
"""


def should_be_escaped(sanitized_chars, string):
    for sanitized_char in sanitized_chars:
        if sanitized_char in string:
            return sanitized_char
    return None


def is_sanitized(request, sanitized_chars, params={}):
    if sanitized_chars is None:
        sanitized_chars = [">", "<"]
    for key, value in params.items():  # Check all get parameters
        escape_char = should_be_escaped(sanitized_chars, value)
        if escape_char and escape_char in request.text:
            print("Unescaped value: " + escape_char + " passed in get param: " + str(
                key) + " found on page: " + request.url)


"""
Checks if an HTTP response code is ok i.e. 200
"""


def is_ok(request, params={}):
    if request.status_code != 200:
        print("Error " + str(request.status_code) + " loading page: " + request.url)
        print("Page called with params: " + str(params))


"""
reads in each line of the file into a list and returns the list
"""


def read_words(filename):
    open_file = open(filename, 'r')
    word_list = open_file.read().split()
    return word_list


"""
Checks if the request text contains any sensitive words
from the sensitive words file.
"""


def contains_sensitive_data(request, sensitive_file, params={}):
    word_list = read_words(sensitive_file)
    sensitive_data_list = []
    for word in word_list:
        if word in request.text:
            sensitive_data_list.append(word)
    if len(sensitive_data_list) > 0:
        print("Sensitive words found using url [" + request.url + "]: " + str(sensitive_data_list))
        if len(params) > 0:
            print("\tPage called with get params: " + str(params))
        print("\n")
    return False


def test(forms, vectors, sanitized_chars, sensitive_file, timeout=500):
    url_list = []
    form_list = []
    for url, form in forms.items():
        url_list.append(url)
        form_list.append(form)
    for url, form_list in zip(url_list, form_list):
        print("Testing forms on " + url)
        form_method = ""
        # should only have 1 form
        for form in form_list:
            form_method = str(form['method']).lower()

            for i in range(0, len(vectors)):

                # find a list of inputs
                inputs = form.findAll('input')

                # build a dictionary of inputs mapped to vectors
                params = {}
                for line in inputs:
                    if 'name' in line.attrs:
                        input_name = line['name']
                    elif 'type' in line.attrs:
                        input_name = line['type']

                    if input_name.lower().strip() == "submit":
                        params[input_name] = "Submit"
                    else:
                        params[input_name] = vectors[i]

                # (timeout is in seconds, not milliseconds)
                try:
                    if form_method == "post":
                        post = browser.open(url, timeout=timeout / 1000)
                        is_ok(post, params=params)
                        contains_sensitive_data(post, sensitive_file, params=params)
                        is_sanitized(post, sanitized_chars, params)
                    elif form_method == "get":
                        get = browser.open(url, timeout=timeout / 1000)
                        is_ok(get, params=params)
                        contains_sensitive_data(get, sensitive_file, params=params)
                        is_sanitized(get, sanitized_chars, params)
                except Exception as e:
                    print(e)
