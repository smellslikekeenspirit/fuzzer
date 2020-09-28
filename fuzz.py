import argparse
import mechanicalsoup

parser = argparse.ArgumentParser()
parser.add_argument("--command", type=str, choices=['discover', 'test'])
parser.add_argument("--url", type=str)
parser.add_argument("--custom-auth", type=str)
args = parser.parse_args()
browser = mechanicalsoup.StatefulBrowser()
url = args.url

if args.command == "discover" and args.custom_auth == "dvwa":
    browser.open("{url}/setup.php".format(url=url, custom_auth=args.custom_auth))
    browser.select_form('form[action="#"]')
    browser.submit_selected()
    browser.open("{url}".format(url=url))
    browser.select_form('form[action="login.php"]')
    browser["username"] = "admin"
    browser["password"] = "password"
    response = browser.submit_selected()
    print(response.text)
    browser.open("{url}/security.php".format(url=url))
    browser.select_form('form[action="#"]')
    browser["security"] = "low"
    browser.submit_selected()
else:
    # assuming we are going to go to fuzzer_tests if we don't have dvwa auth
    browser.open(url)
    browser.select_form('form[action="/fuzzer-tests/index.php"]')
    browser["calzone"] = "chicken bacon ranch"
    # just to see if the text has been put into the textbox"
    browser.launch_browser()
    browser.submit_selected()
