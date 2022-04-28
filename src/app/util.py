from fastapi import HTTPException
import iconclass
import urllib.parse
import re, os, sqlite3
from typing import List
from enum import Enum
import smtplib
from email.message import EmailMessage
import httpx

KEYS_RE = r"^\w*\(\+"

# Tip: to run it, do
# >>> import asyncio
# >>> asyncio.run(app.util.get_wikidata("73D24"))
async def get_wikidata(notation: str):
    query = (
        """
SELECT DISTINCT (SAMPLE(?item) AS ?i) ?itemLabel (SAMPLE(?pic) as ?picture)
WHERE
{
?item wdt:P1257 "%s" .
?item wdt:P18 ?pic
SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
} GROUP BY ?itemLabel
ORDER BY ?itemLabel
"""
        % notation
    )

    with httpx.Client() as client:
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "ICONCLASS/2021 (https://test.iconclass.org/ info@iconclass.org)",
        }
        r = client.get(
            "https://query.wikidata.org/sparql?query=" + urllib.parse.quote_plus(query),
            headers=headers,
        )
    return r.json()


def get_image_path_count(notation: str) -> List:
    if notation.endswith("...)"):
        notation = notation[:-4]
    IC_PATH = os.environ.get("IC_PATH", "iconclass.sqlite")
    index_db = sqlite3.connect(IC_PATH)
    cur = index_db.cursor()
    cur.execute(
        "SELECT count(image) FROM images i INNER JOIN images_ic ii ON ii.id = i.id WHERE ii.notation LIKE ?",
        (notation + "%",),
    )
    results = cur.fetchone()
    return results[0]


LANGUAGES = {
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "it": "Italiano",
    "pt": "Portuguese",
    "fi": "Finnish",
    "nl": "Nederlands",
    "zh": "中文",
    "ja": "日本語",
}


def valid_lang(lang):
    if lang not in ("en", "de", "fr", "it", "pt", "nl", "pl", "zh", "fi", "jp"):
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

    #    obj["image_count"] = get_image_path_count(obj["n"])
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


class SearchSortOptions(Enum):
    RANK = "rank"
    NOTATION = "notation"


# User-defined function for regex in the sqlite database
def regexp(pattern, value):
    matcher = re.compile(pattern)
    if matcher.match(value):
        return True
    else:
        return False


def do_search(q: str, lang: str, sort: str, keys: bool, r: str):
    ##TODO
    # sort is either "rank" or "notation" : this needs to be expressed in the parameter as an enumeration.
    # How to do this properly?
    try:
        sort = SearchSortOptions(sort)
    except ValueError:
        sort = SearchSortOptions("rank")
    if lang not in ("en", "de", "fr", "it"):
        raise HTTPException(
            status_code=404,
            detail=f"Language [{lang}] can not be searched in at the moment",
        )

    IC_INDEX_PATH = os.environ.get("IC_INDEX_PATH", "iconclass_index.sqlite")
    index_db = sqlite3.connect(IC_INDEX_PATH)
    index_db.enable_load_extension(True)
    index_db.load_extension("/usr/local/lib/fts5stemmer")
    index_db.create_function("regexp", 2, regexp)
    cur = index_db.cursor()

    if keys:
        keys = ""
    else:
        keys = "is_key=0 AND "
    if q:
        if q[0] in "0123456789":
            SQL = f"SELECT notation FROM notations WHERE notation like ? order by notation"
            if not q.endswith("%"):
                q = q + "%"
        else:
            SQL = f"SELECT notation FROM {lang} WHERE {keys}text MATCH ? order by {sort.value}"
    else:
        SQL = f"SELECT notation FROM notations WHERE notation REGEXP ?"
        q = r
    try:
        if len(r) > 0:
            rr = re.compile(r)
            results = [x[0] for x in cur.execute(SQL, (q,)) if rr.match(x[0])]
        else:
            results = [x[0] for x in cur.execute(SQL, (q,))]
    except sqlite3.OperationalError:
        results = []
    return results


def send_email(sender: str, receiver: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.set_content(body)
    s = smtplib.SMTP("localhost")
    s.send_message(msg)
    s.quit()


def get_random_notations(count: int = 1):
    SQL = f"select notation from notations ORDER BY RANDOM() LIMIT {count}"
    IC_PATH = os.environ.get("IC_PATH", "iconclass.sqlite")
    cur = sqlite3.connect(IC_PATH).cursor()
    try:
        results = [x[0] for x in cur.execute(SQL)]
    except sqlite3.OperationalError:
        results = ["0"]
    return results
