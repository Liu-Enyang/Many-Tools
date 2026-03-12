from bs4 import BeautifulSoup


def heal_selector(selector, html):

    soup = BeautifulSoup(html, "html.parser")

    if selector.startswith("#"):

        el = soup.find(id=selector[1:])

        if el:
            return selector

    # fallback by name

    name = selector.replace("#", "")

    el = soup.find(attrs={"name": name})

    if el:
        return f"[name='{name}']"

    return selector