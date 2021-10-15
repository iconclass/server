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
            lastp = p[-1]
        elif p1.startswith("(") and p1.endswith(")"):
            if p1 != "(...)":
                p.append(lastp + "(...)")
            p.append(lastp + p1)
            lastp = p[-1]
        else:
            for x in range(len(p1)):
                p.append(lastp + p1[x])
                if len(p) > 0:
                    lastp = p[len(p) - 1]
    return p


CACHE = {}


def reset_fontsizes():
    for notation_element in CACHE.values():
        notation_element.element.classList.remove("active_notation")


def got_nav_results(result):
    # go through the path of objects in result, and add them to the CACHE tree
    result = dict(result)
    for obj in result.get("result", []):
        parent = obj["p"][len(obj["p"]) - 2]
        CACHE[obj["n"]] = NotationElement(CACHE[parent].element, obj["n"], obj, True)
    reset_fontsizes()


def nav_in_tree(event):
    event.preventDefault()
    desired = event.target.getAttribute("data-notation")
    params = "&".join(
        [
            "notation=" + encodeURIComponent(p)
            for p in get_parts(desired)
            if p not in CACHE
        ]
    )
    fetch("/json?" + params).then(
        lambda response: response.json().then(got_nav_results)
    )


class NotationElement:
    def __init__(self, parent_element, notation, obj=None, showkids=False):
        self.parent_element = parent_element
        self.notation = notation
        self.expanded = showkids == True
        nuri = "/{}.json".format(encodeURIComponent(notation))
        if obj:
            self.got_json_obj(obj, showkids)
        else:
            fetch(nuri).then(self.got_init_response)
        # Also fetch the focus fragment
        self.focus_text = "<p>...pending...</p>"
        furi = "/fragments/focus/{}/{}".format(
            document.IC_LANG, encodeURIComponent(notation)
        )
        fetch(furi).then(self.got_fragment_focus)

    def got_fragment_focus(self, response):
        response.text().then(self.got_fragment_focus_text)

    def got_fragment_focus_text(self, result):
        self.focus_text = result

    def got_init_response(self, response):
        response.json().then(self.got_json_obj)

    def got_children_response(self, response):
        response.json().then(self.got_json_objs_results)

    def got_json_objs_results(self, result):
        result = dict(result)
        tmp_map = {}
        for x in result.get("result", []):
            tmp_map[x["n"]] = x
        for c in self.children:
            if c in tmp_map:
                CACHE[c] = NotationElement(self.kids_element, c, tmp_map[c])

    def got_json_obj(self, obj, showkids=False):
        obj = dict(obj)
        txts = dict(obj.get("txt", {}))
        kws = dict(obj.get("kw", {}))
        self.children = obj.get("c", [])
        expanda = Span(
            self.notation,
            id="x" + self.notation,
            style={"cursor": "pointer"},
            _class="notation_n",
        )

        self.parent_element.insertAdjacentHTML(
            "beforeend",
            Div(
                Div(
                    expanda,
                    Span(txts.get(document.IC_LANG, ""), _class="notation_txt"),
                    id=self.notation,
                    _class="notation_container",
                ),
                Div(id="kids_" + self.notation),
                style={"padding-left": "10px"},
            ).render(),
        )
        expander = document.getElementById("x" + self.notation)
        expander.addEventListener("click", self.expand)
        self.element = document.getElementById(self.notation)
        self.kids_element = document.getElementById("kids_" + self.notation)

        if showkids:

            class E:
                target = expander

            self.expand(E())

    def expand(self, event):
        if self.expanded:
            self.kids_element.style.display = "none"
            self.element.classList.remove("open_notation")
        else:
            reset_fontsizes()
            self.element.classList.add("active_notation")
            self.element.classList.add("open_notation")
            self.kids_element.style.display = "block"
            # If any of self.c in CACHE, we have already fetched the kids don't do it again
            if self.children[0] not in CACHE:
                params = "&".join(
                    [
                        "notation=" + encodeURIComponent(c)
                        for c in self.children
                        if c.find("(+") < 0
                    ]
                )
                fetch("/json?" + params).then(self.got_children_response)
            # set the focus fragment
            results = document.getElementById("results")
            results.innerHTML = self.focus_text
            # find all the current items that need nav, and set their handlers
            for navver in results.getElementsByClassName("navver"):
                navver.addEventListener("click", nav_in_tree)

        self.expanded = not self.expanded


thetree = document.getElementById("thetree")

for n in "0123456789":
    thetree.insertAdjacentHTML("beforeend", "<div id='tree" + n + "'/>")
    element = document.getElementById("tree" + n)
    CACHE[n] = NotationElement(element, n)
