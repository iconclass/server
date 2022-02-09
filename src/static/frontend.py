from htmltree import *

NODE_MAP = {}
caret_right_fill = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-right-fill" viewBox="0 0 16 16">
  <path d="m12.14 8.753-5.482 4.796c-.646.566-1.658.106-1.658-.753V3.204a1 1 0 0 1 1.659-.753l5.48 4.796a1 1 0 0 1 0 1.506z"/>
</svg>"""
caret_down_fill = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-down-fill" viewBox="0 0 16 16">
  <path d="M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z"/>
</svg>"""
dot = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-dot" viewBox="0 0 16 16">
  <path d="M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/>
</svg>"""


async def get_obj(anid):
    if anid in NODE_MAP:
        obj = dict(NODE_MAP[anid])
        # if obj.isFat == True:
        return obj
    result = await fetch("/" + anid + ".fat")  # TODO handle 404
    response = await result.json()
    obj = dict(response)
    # obj.isFat = True
    NODE_MAP[anid] = obj
    # for c in obj.get("c", []):
    #     c.isFat = False
    #     NODE_MAP[c["n"]] = c
    return obj


def find_attr_parents(element, attr):
    val = element.getAttribute(attr)
    if val and len(val) > 0:
        return val
    parent = element.parentElement
    if parent:
        return find_attr_parents(parent, attr)


async def add_desired_to_tree(notation):
    results_element = document.getElementById("results")
    results_element.innerHTML = '<div style="margin-top: 20px" class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>'

    node = await get_obj(notation)
    pad = [x["n"] for x in node.get("p") if x["n"] != notation]
    await build("ICONCLASS", thetree_element, pad)
    await focus_node(notation)


async def build(anid, an_element, path=[]):
    node = await get_obj(anid)

    for kind in node.get("c", []):
        kind_node = await get_obj(kind["n"])
        k_n = kind["n"]

        if k_n in path:
            kids_display = "block"
        else:
            kids_display = "none"

        node_style = {"padding-left": "1ch", "cursor": "pointer"}
        if k_n.find("(+") > 0:
            # This is a key
            node_style["display"] = "none"

        if kind_node.kids_element:
            # We have already added this child
            kind_node.kids_element.style.display = "block"
        else:
            # Exclude the keys as children to determine icon
            kids_without_keys = [
                kn for kn in kind_node.get("c", []) if kn["n"].find("(+") < 1
            ]

            if len(kids_without_keys) > 0:
                kind_icon = caret_right_fill
            else:
                kind_icon = dot
            display_txt = (
                k_n + " &middot; " + dict(kind["txt"]).get(document.IC_LANG, "")
            )

            an_element.insertAdjacentHTML(
                "beforeend",
                Div(
                    Span(
                        kind_icon,
                        id="icon" + k_n,
                        anid=k_n,
                        style={"margin-right": "0.6ch"},
                    ),
                    Span(display_txt, anid=k_n, id="text" + k_n, _class="notationtext"),
                    Div(id="kids" + k_n, style={"display": kids_display}),
                    id=k_n,
                    style=node_style,
                    anid=k_n,
                ).render(),
            )
            kind_node.fragment = None
            kind_node.element = document.getElementById(k_n)
            kind_node.kids_element = document.getElementById("kids" + k_n)
            kind_node.text_element = document.getElementById("text" + k_n)
        if k_n in path:
            await build(k_n, kind_node.kids_element, path)


async def focus_node(desired):
    if desired not in NODE_MAP:
        return
    history.pushState({}, "", "/" + encodeURIComponent(desired))
    node = NODE_MAP[desired]

    kids_element = document.getElementById("kids" + desired)
    icon_element = document.getElementById("icon" + desired)
    text_element = document.getElementById("text" + desired)

    # Some notations, like 11II321 has a "virtual" double key.
    # In its path, ['1', '11', '11I', '11II', '11II3', '11II32', '11II321']
    # the notation 11II does not actually exist
    # But we still want to be able to focus and display these.

    if kids_element:
        # Exclude the keys as children to determine icon
        kids_without_keys = [kn for kn in node.get("c", []) if kn["n"].find("(+") < 1]
        if len(kids_without_keys) > 0:
            kind_icon = None
        else:
            kind_icon = dot
        if kids_element.style.display == "none":
            kids_element.style.display = "block"
            icon_element.innerHTML = kind_icon or caret_down_fill
        else:
            kids_element.style.display = "none"
            icon_element.innerHTML = kind_icon or caret_right_fill

    if not node.fragment:
        furi = "/fragments/focus/{}/{}".format(
            document.IC_LANG, encodeURIComponent(desired)
        )
        result = await fetch(furi)
        response = await result.text()
        node.fragment = response
        if len(node["c"]) > 0 and kids_element:
            await build(desired, kids_element)

    results_element.innerHTML = node.fragment

    for notationtext in document.querySelectorAll(".notationtext"):
        notationtext.classList.remove("focussed")
    if text_element:
        text_element.classList.add("focussed")

    try:
        node.element.scrollIntoViewIfNeeded()  # This is a proprietary method does not work on all browsers
    except:
        pass


async def show_object(anid):
    furi = "/fragments/object/{}/".format(encodeURIComponent(anid))
    result = await fetch(furi)
    response = await result.text()
    results_element.innerHTML = response


async def tree_clicker(event):
    desired = find_attr_parents(event.target, "anid")
    if len(desired) > 0:
        focus_node(desired)


async def focussed_results_clicker(event):
    results_clicker(event)
    navtabNavigate_click()


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


def get_searchoption_opposite(value):
    if value == "1":
        return "0"
    if value == "0":
        return "1"
    if value == "rank":
        return "notation"
    if value == "notation":
        return "rank"


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


results_element = document.getElementById("results")
results_element.addEventListener("click", focussed_results_clicker)
thetree_element = document.getElementById("thetree")
thetree_element.addEventListener("click", tree_clicker)

if document.notation and document.notation != "_":
    add_desired_to_tree(document.notation)
else:
    build("ICONCLASS", thetree_element)
