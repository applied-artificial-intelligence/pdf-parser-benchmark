The structure of the search results can be examined with your browser tools, as shown here:

Here, we see that the search results are structured as links whose parent element is a <h3> tag with class "r".

To scrape the search results, we will use a CSS selector, which was introduced in Chapter 2, Scraping the Data:

">>> from lxml.html import fromstring\n>>> import requests\n>>> html = requests.get('https://www.google.com/search?q=test')\n>>> tree = fromstring(html.content)\n>>> results = tree.cssselect('h3.r a')\n>>> results\n[<Element a at 0x7f3d9affeaf8>, <Element a at 0x7f3d9affe890>, <Element a at 0x7f3d9affe8e8>, <Element a at 0x7f3d9affeaa0>, <Element a at 0x7f3d9b1a9e68>, <Element a at 0x7f3d9b1a9c58>, <Element a at 0x7f3d9b1a9ec0>, <Element a at 0x7f3d9b1a9f18>, <Element a at 0x7f3d9b1a9f70>, <Element a at 0x7f3d9b1a9fc8>]"

[183]

Putting It All Together