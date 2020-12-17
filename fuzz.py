import argparse
import mechanicalsoup
from tests import test

parser = argparse.ArgumentParser()
parser.add_argument("--command", type=str, choices=['discover', 'test'])
parser.add_argument("--url", type=str)
parser.add_argument("--custom-auth", type=str)
parser.add_argument("--common-words", type=str)
parser.add_argument("--extensions", type=str)
parser.add_argument("--vectors", type=str)
parser.add_argument("--sensitive", type=str)
parser.add_argument("--sanitized-chars", type=str)
parser.add_argument("--slow", type=int)



args = parser.parse_args()
browser = mechanicalsoup.StatefulBrowser()
url = args.url


def discover_pages():
    """
    guesses page names through common word and inner links
    :return: list of links
    """
    common_words = []
    file = open(args.common_words, "r")
    for line in file:
        common_words.append(line.strip())

    # use defaults if no file provided
    extensions = []
    if not args.extensions:
        extensions = [".php", ""]
    else:
        with open(args.extensions, "r") as file:
            for line in file:
                extensions.append(line.strip())

    links_that_exist = {}
    for word in common_words:
        for extension in extensions:
            test_link = "{url}/{word}{extension}".format(url=args.url, word=word, extension=extension)
            if test_link not in links_that_exist.keys() or links_that_exist[test_link] == 0:
                if browser.open(test_link).status_code == 200:
                    # 1 to represent visited link and 0 for not visited
                    links_that_exist[test_link] = 1
                    found_links = browser.get_current_page().find_all('a')
                    for link in found_links:
                        href = link.get('href')
                        if href and "logout" not in href:
                            test_link = "{url}/{href}".format(url=args.url, href=href)
                            if browser.open(test_link).status_code == 200:
                                links_that_exist[test_link] = 0

    # counter for links that have not been visited
    new = 0
    for value in links_that_exist.values():
        if value == 0:
            new += 1
    # run while all links have been visited
    while new != 0:
        for key in list(links_that_exist.keys()):
            # if not visited yet, mark as visited
            if links_that_exist[key] == 0:
                new -= 1
                links_that_exist[key] = 1
                # if valid webpage, visit to find inner links
                if browser.open(key).status_code == 200:
                    if browser.get_current_page():
                        found_links = browser.get_current_page().find_all('a')
                        for link in found_links:
                            href = link.get('href')
                            if href and "logout" not in href:
                                test_link = "{url}/{href}".format(url=args.url, href=href)
                                if links_that_exist.get(test_link) is None and browser.open(test_link).status_code == 200:
                                    new += 1
                                    links_that_exist[test_link] = 0
    # printing all links found finally
    for key, value in links_that_exist.items():
        print(key, ' : ', value)
    return list(links_that_exist.keys())


def print_with_tabs(string, tabs):
    print("\t" * tabs + string)


def discover_input(page):
    """
    finds all input pathways into a page
    :param page: page url
    :return:
    """
    browser.open(page)
    if browser.get_current_page():
        print(browser.get_current_page().find_all('input'))


def discover_cookies():
    """
    prints all cookies
    :return:
    """
    for cookie in browser.get_cookiejar():
        print(cookie)


def discover_forms(urls):
    forms = {}

    for url in urls:
        browser.open(url)
        if browser.get_current_page():
            print("Discovering forms in " + url)
            forms[url] = browser.get_current_page().findAll('form')
            for form in forms[url]:
                print("form method=\"" + form["method"] + "\" found on " + url)
                for input_tag in form.recursiveChildGenerator():
                    if input_tag.name == "input":
                        if "name" in input_tag.attrs:
                            print_with_tabs("input tag name=" + "\"" + input_tag["name"] + "\"", 1)
                        elif "value" in input_tag.attrs:
                            print_with_tabs("input tag value=" + "\"" + input_tag["value"] + "\"", 1)
                        else:
                            print_with_tabs(input_tag)
    return forms


def dvwa_auth():
    browser.open("{url}".format(url=url))
    browser.select_form('form[action="login.php"]')
    browser["username"] = "admin"
    browser["password"] = "password"
    response = browser.submit_selected()
    browser.open("{url}/security.php".format(url=url))
    browser.select_form('form[action="#"]')
    browser["security"] = "low"
    browser.submit_selected()


def main():
    """
    runs functions according to given args
    :return:
    """
    if args.command == "discover" and args.custom_auth == "dvwa":
        print("{url}/setup.php".format(url=url))
        browser.open("{url}/setup.php".format(url=url))
        browser.select_form('form[action="#"]')
        browser.submit_selected()
        dvwa_auth()
        if args.common_words:
            links = discover_pages()
            print("Links found --------------------------------------------------------------------")
            for link in links:
                print(link)
                print("Inputs in link -------------------------------------------------------------")
                discover_input(link)
            print("Cookies ------------------------------------------------------------------------")
            discover_cookies()
    elif args.command == "test":
        dvwa_auth()
        links = discover_pages()
        print(links)
        forms = discover_forms(links)
        vectors = open(args.vectors).readlines()
        sanitized_chars = None
        if args.sanitized_chars:
            sanitized_chars = open(args.sanitized_chars).readlines()
        sensitive_file = args.sensitive
        if args.slow:
            test(forms, vectors, sanitized_chars, sensitive_file, args.slow)
        else:
            test(forms, vectors, sanitized_chars, sensitive_file)
    else:
        # assuming we are going to go to fuzzer_tests if we don't have dvwa auth
        browser.open("{url}".format(url=url))
        browser.select_form('form[action="/fuzzer-tests/index.php"]')
        browser["calzone"] = "chicken bacon ranch"
        # just to see if the text has been put into the textbox"
        browser.launch_browser()
        browser.submit_selected()
        browser.open(url)
        if args.common_words:
            links = discover_pages()
            print(links)
            for link in links:
                discover_input(link)
            discover_cookies()


if __name__ == '__main__':
    main()
