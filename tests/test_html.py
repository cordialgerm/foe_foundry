from bs4 import BeautifulSoup

from foe_foundry.utils.html import fix_relative_paths, remove_h2_sections


def test_beautiful_soup_equality():
    html1 = "<div>    Hello World</div>"
    html2 = "\n\n<div>Hello World</div>"
    soup1 = BeautifulSoup(html1, "html.parser").prettify()
    soup2 = BeautifulSoup(html2, "html.parser").prettify()
    assert soup1 == soup2, f"Expected {soup1} to equal {soup2}"


def test_remove_h2_sections():
    html = """
    <html>
        <body>
            <h2 id="section1">Section 1</h2>
            <p>This is some text in section 1.</p>
            <h2 id="section2">Section 2</h2>
            <p>This is some text in section 2.</p>
            <h2 id="section3">Section 3</h2>
            <p>This is some text in section 3.</p>
        </body>
    </html>
    """
    h2_ids_to_remove = ["section1", "section3"]
    expected_output = """
    <html>
        <body>
            <h2 id="section2">Section 2</h2>
            <p>This is some text in section 2.</p>
        </body>
    </html>
    """.strip()

    result = remove_h2_sections(html, h2_ids_to_remove)

    soup1 = BeautifulSoup(result, "html.parser").prettify()
    soup2 = BeautifulSoup(expected_output, "html.parser").prettify()
    assert soup1 == soup2, f"Expected {soup1} to equal {soup2}"


BASE = "/docs/some-page"


def get_attr(html, tag, attr):
    soup = BeautifulSoup(html, "html.parser")
    return [el[attr] for el in soup.find_all(tag) if attr in el.attrs]


def test_relative_img_src():
    html = '<img src="images/foo.png">'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "img", "src") == ["/docs/some-page/images/foo.png"]


def test_absolute_img_src_unchanged():
    html = '<img src="/assets/foo.png">'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "img", "src") == ["/assets/foo.png"]


def test_external_link_unchanged():
    html = '<a href="https://example.com">Link</a>'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "a", "href") == ["https://example.com"]


def test_relative_link():
    html = '<a href="page2.html">Next</a>'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "a", "href") == ["/docs/some-page/page2.html"]


def test_script_src():
    html = '<script src="js/main.js"></script>'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "script", "src") == ["/docs/some-page/js/main.js"]


def test_link_href():
    html = '<link href="styles/site.css" rel="stylesheet">'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "link", "href") == ["/docs/some-page/styles/site.css"]


def test_srcset_handling():
    html = '<img srcset="img/foo-1x.png 1x, img/foo-2x.png 2x">'
    result = fix_relative_paths(html, BASE)
    soup = BeautifulSoup(result, "html.parser")
    tag = soup.find("img")
    assert (
        tag["srcset"]
        == "/docs/some-page/img/foo-1x.png 1x, /docs/some-page/img/foo-2x.png 2x"
    )


def test_data_url_ignored():
    html = '<img src="data:image/png;base64,ABCDEF==">'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "img", "src")[0].startswith("data:image/png")


def test_fragment_link_ignored():
    html = '<a href="#section">Jump</a>'
    result = fix_relative_paths(html, BASE)
    assert get_attr(result, "a", "href") == ["#section"]
