from htmltree import *
import re

SPLITTER = re.compile(r"(\(.+?\))")


def get_parts(a):
    "Split an ICONCLASS notation up into a list of its parts"
    p = []
    lastp = ""
    for p1 in SPLITTER.split(a):
        if p1.startswith("(+"):
            tmplastp = lastp + "(+"
            for x in p1[2:]:
                if x and x != ")":
                    p.append(tmplastp + x + ")")
                    tmplastp += x
            lastp = p[len(p) - 1]
        elif p1.startswith("(") and p1.endswith(")"):
            if p1 != "(...)":
                p.append(lastp + "(...)")
            p.append(lastp + p1)
            lastp = p[len(p) - 1]
        else:
            for x in range(len(p1)):
                p.append(lastp + p1[x])
                if len(p) > 0:
                    lastp = p[len(p) - 1]
    return p


NODE_MAP = {}


def add_desired_to_tree(notation):
    results_element = document.getElementById("results")
    results_element.innerHTML = '<div style="margin-top: 20px" class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>'

    parts = get_parts(notation)
    last_part = NODE_MAP[
        parts[0]
    ]  # We are going to assume all the root nodes are in there already
    for part in parts:
        if part not in NODE_MAP:
            build(last_part, last_part.kids_element, parts)
            break
        else:
            last_part = NODE_MAP[part]
            last_part.kids_element.style.display = "block"
            last_part.element.classList.add("open_notation")

    setTimeout(lambda x: focus_node(notation), 500)


def get_searchoption_opposite(value):
    if value == "1":
        return "0"
    if value == "0":
        return "1"
    if value == "rank":
        return "notation"
    if value == "notation":
        return "rank"


async def results_clicker(event):
    # handle the search option buttons
    if event.target.id == "includekeys":
        q = document.getElementById("searchbox").value
        searchsortorder = document.getElementById("searchsortorder").getAttribute(
            "data"
        )
        includekeys = document.getElementById("includekeys").getAttribute("data")
        dosearch(q, includekeys, get_searchoption_opposite(searchsortorder))
        return
    if event.target.id == "searchsortorder":
        q = document.getElementById("searchbox").value
        includekeys = document.getElementById("includekeys").getAttribute("data")
        searchsortorder = document.getElementById("searchsortorder").getAttribute(
            "data"
        )
        dosearch(q, get_searchoption_opposite(includekeys), searchsortorder)
        return
    if event.target.id == "advancedsearch":
        sre = document.getElementById("searchregex")
        sre.style.display = "block"
        sre.focus()
        advs = document.getElementById("advancedsearch")
        advs.style.display = "none"
        return
    if event.target.classList.contains("kw_search"):
        kw = event.target.getAttribute("data")
        if kw.find(" ") > -1:
            kw = '"' + kw + '"'

        navtabSearch_click(None)
        searchsortorder = document.getElementById("searchsortorder").getAttribute(
            "data"
        )
        dosearch(
            kw,
            "0",
            get_searchoption_opposite(searchsortorder),
        )
        document.getElementById("searchbox").value = kw
        return
    desired = event.target.getAttribute("notation")
    if len(desired) < 1:
        return
    if desired:
        add_desired_to_tree(desired)


async def tree_clicker(event):
    desired = event.target.getAttribute("notation")
    if len(desired) > 0:
        focus_node(desired)


async def focus_node(desired):
    if desired not in NODE_MAP:
        return
    history.pushState({}, "", "/" + encodeURIComponent(desired))
    node = NODE_MAP[desired]
    if node.fragment is None:
        furi = "/fragments/focus/{}/{}".format(
            document.IC_LANG, encodeURIComponent(desired)
        )
        result = await fetch(furi)
        response = await result.text()
        node.fragment = response
        if len(node["c"]) > 0:
            new_element = document.getElementById("kids" + desired)
            build(node, new_element)

    # set the focus fragment
    results_element = document.getElementById("results")
    results_element.innerHTML = node.fragment

    for anode in NODE_MAP.values():
        anode.element.classList.remove("active_notation")
    node.element.classList.add("active_notation")

    if len(node["c"]) > 0:
        kid_element = document.getElementById("kids" + desired)
        if kid_element.style.display == "block":
            kid_element.style.display = "none"
            node.element.classList.remove("open_notation")
        else:
            kid_element.style.display = "block"
            node.element.classList.add("open_notation")


async def build(node, an_element, path=[]):

    # Fetch the IC object for this node
    result = await fetch("/" + node["n"] + ".fat")
    response = await result.json()
    response = dict(response)

    for kind in response.get("c", []):
        k_n = kind["n"]
        if k_n.find("(+") > 0:
            # This is a key
            k_display = "none"
        else:
            k_display = "block"
        NODE_MAP[k_n] = kind
        kind.fragment = None
        if k_n in path:
            kids_display = "block"
        else:
            kids_display = "none"

        display_txt = k_n + " &middot; " + dict(kind["txt"]).get(document.IC_LANG, "")
        an_element.insertAdjacentHTML(
            "beforeend",
            Div(
                Span(display_txt, _class="ntext", notation=k_n),
                Div(id="kids" + k_n, style={"display": kids_display}),
                id=k_n,
                style={
                    "padding-left": "5px",
                    "cursor": "pointer",
                    "display": k_display,
                },
                notation=k_n,
            ).render(),
        )
        kind.element = document.getElementById(k_n)
        kind.kids_element = document.getElementById("kids" + k_n)
        if k_n in path:
            build(kind, kind.kids_element, path)


iconclass_tree = {"n": "ICONCLASS", "c": []}
document.iconclass_tree = iconclass_tree

thetree_element = document.getElementById("thetree")
thetree_element.addEventListener("click", tree_clicker)
build(iconclass_tree, thetree_element)

# Check to see if the document was called with an initial notation, if so browse to it
if document.notation and document.notation != "_":
    setTimeout(lambda x: add_desired_to_tree(document.notation), 750)
# See if the document was called with a q search parameter, if so do the search
if document.q:
    setTimeout(lambda x: search_action(), 750)

document.getElementById("results").addEventListener("click", results_clicker)

searchtab_element = document.getElementById("searchtab")
searchresults_element = document.getElementById("searchresults")
searchtab_element.addEventListener("click", results_clicker)

navtabNavigate = document.getElementById("navtabNavigate")
navtabSearch = document.getElementById("navtabSearch")


def navtabNavigate_click(event):
    thetree_element.style.display = "block"
    searchtab_element.style.display = "none"
    navtabNavigate.classList.add("active")
    navtabSearch.classList.remove("active")


navtabNavigate.addEventListener("click", navtabNavigate_click)


def navtabSearch_click(event):
    thetree_element.style.display = "none"
    searchtab_element.style.display = "block"
    navtabSearch.classList.add("active")
    navtabNavigate.classList.remove("active")


navtabSearch.addEventListener("click", navtabSearch_click)


########## Handle searchbox


async def dosearch(q, keys, sort):
    searchresults_element.innerHTML = '<div style="margin-top: 20px" class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>'

    search_url = (
        "/fragments/search/"
        + document.IC_LANG
        + "/?q="
        + encodeURIComponent(q)
        + "&sort="
        + sort
        + "&keys="
        + keys
        + "&r="
        + encodeURIComponent(document.getElementById("searchregex").value)
    )
    result = await fetch(search_url)
    response = await result.text()
    searchresults_element.innerHTML = response
    searchtab_element.style.display = "block"
    thetree_element.style.display = "none"
    navtabNavigate.classList.remove("active")
    navtabSearch.classList.add("active")


async def search_action():
    q = document.getElementById("searchbox").value
    includekeys = document.getElementById("includekeys").getAttribute("data")
    searchsortorder = document.getElementById("searchsortorder").getAttribute("data")

    dosearch(
        q,
        get_searchoption_opposite(includekeys),
        get_searchoption_opposite(searchsortorder),
    )


async def searchbox_keyup(event):
    if event.keyCode == 13:
        search_action()


document.getElementById("searchbox").addEventListener("keyup", searchbox_keyup)


async def searchregex_keyup(event):
    if event.keyCode == 13:
        search_action()


document.getElementById("searchregex").addEventListener("keyup", searchregex_keyup)
