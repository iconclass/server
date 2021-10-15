import iconclass
import urllib.parse
import re

KEYS_RE = r"^\w*\(\+"


def valid_lang(lang):
    if lang not in ("en", "de", "fr", "it", "pt", "nl", "pl", "zh", "fi", "ja"):
        lang = "en"
    return lang


def fill_obj(obj):
    if not obj:
        return
    # Add a synthetic item for the keys and with-names , by pre-filtering on items
    k = [k for k in obj.get("c", []) if re.match(KEYS_RE, k)]
    if k:
        obj["k"] = k

    kws_path = {}
    for thing in ("p", "c", "r", "k"):
        tmp = list(filter(None, [iconclass.get(x) for x in obj.get(thing, [])]))
        obj[thing] = tmp
        if thing in ("p", "r"):
            for t in tmp:
                for lang, tt in t.get("kw", {}).items():
                    kws_path.setdefault(lang, []).extend(
                        tt
                    )  # Note, tt is a list of keywords

    # Get all the keywords from the whole path, and make them unique, plus sorted
    if kws_path:
        for lang, kws in kws_path.items():
            obj.setdefault("kws_all", {})[lang] = sorted(set(kws))

    return obj


# Given Iconclass obj. convert it into an ntriple
# See: https://en.wikipedia.org/wiki/N-Triples
def n_to_url(notation):
    return "<http://iconclass.org/%s>" % urllib.parse.quote(notation)


def to_skos_ntriple(obj):
    buf = []
    ba = buf.append
    sub = n_to_url(obj["n"])

    def ba(p, o):
        buf.append("%s %s %s" % (sub, p, o))

    ba(
        "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
        "<http://www.w3.org/2004/02/skos/core#Concept>",
    )
    ba(
        "<http://www.w3.org/2004/02/skos/core#inScheme>",
        "<http://iconclass.org/rdf/2011/09/>",
    )
    if obj.get("p"):
        ba("<http://www.w3.org/2004/02/skos/core#broader>", n_to_url(obj["p"][-1]))
    for c in obj.get("c"):
        ba("<http://www.w3.org/2004/02/skos/core#narrower>", n_to_url(c))
    ba(
        "<http://www.w3.org/2004/02/skos/core#notation>",
        '"%s"' % obj["n"].encode("unicode-escape").decode("ascii"),
    )
    for lan, txt in obj.get("txt").items():
        ba(
            "<http://www.w3.org/2004/02/skos/core#prefLabel>",
            '"%s"@%s' % (txt.encode("unicode-escape").decode("ascii"), lan),
        )
    for lan, kws in obj.get("kw").items():
        for kw in kws:
            ba(
                "<http://purl.org/dc/elements/1.1/subject>",
                '"%s"@%s' % (kw.encode("unicode-escape").decode("ascii"), lan),
            )
    return "\n".join(buf).encode("ascii")
