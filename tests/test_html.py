from bs4 import BeautifulSoup

from foe_foundry.utils.html import remove_h2_sections


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
