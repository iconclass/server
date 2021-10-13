from htmltree import *

CACHE = {}


def reset_fontsizes():
    for notation_element in CACHE.values():
        notation_element.element.classList.remove("active_notation")


class NotationElement:
    def __init__(self, parent_element, notation, obj=None, showkids=False):
        self.parent_element = parent_element
        self.notation = notation
        self.expanded = False
        self.expanda_closed = "&middot; " + self.notation
        self.expanda_open = "&middot; " + self.notation
        nuri = "/{}.json".format(encodeURIComponent(notation))
        if obj:
            self.got_json_obj(obj, showkids)
        else:
            fetch(nuri).then(self.got_init_response)

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
        if len(self.children) > 0:
            self.expanda_closed = "&vellip; " + self.notation
            self.expanda_open = "&dtdot;" + self.notation
        expanda = Span(
            self.expanda_closed,
            id="x" + self.notation,
            style={"cursor": "pointer"},
            _class="notation_n",
        )

        details = Div(
            Span(
                ", ".join([kw for kw in kws.get(document.IC_LANG, [])]),
                _class="details_keywords",
            ),
            _class="details",
        )
        if len(obj.get("r", [])) > 0:
            details.C.append(Div("Also:" + ", ".join([r for r in obj.get("r", [])])))

        self.parent_element.insertAdjacentHTML(
            "beforeend",
            Div(
                Div(
                    expanda,
                    Span(txts.get(document.IC_LANG, ""), _class="notation_txt"),
                    details,
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
            event.target.innerHTML = self.expanda_closed
            self.kids_element.style.display = "none"
        else:
            reset_fontsizes()
            self.element.classList.add("active_notation")
            event.target.innerHTML = self.expanda_open
            # self.kids_element.style.display = "block"
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

        self.expanded = not self.expanded


CACHE["ICONCLASS"] = NotationElement(
    document.getElementById("thetree"),
    "ICONCLASS",
    {"n": "", "c": [str(x) for x in range(10)], "txt": {}},
    True,
)
