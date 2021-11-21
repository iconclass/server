import iconclass
import urllib.parse
import re, os, sqlite3
from typing import List
import smtplib
from email.message import EmailMessage

KEYS_RE = r"^\w*\(\+"


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


def do_search(q: str, lang: str, sort: str, keys: bool):
    if lang not in ("en", "de"):
        lang = "en"
    IC_INDEX_PATH = os.environ.get("IC_INDEX_PATH", "iconclass_index.sqlite")
    index_db = sqlite3.connect(IC_INDEX_PATH)
    index_db.enable_load_extension(True)
    index_db.load_extension("/usr/local/lib/fts5stemmer")
    cur = index_db.cursor()

    if keys:
        SQL = f"SELECT notation FROM {lang} WHERE text MATCH ? order by {sort}"
    else:
        SQL = f"SELECT notation FROM {lang} WHERE is_key=0 AND text MATCH ? order by {sort}"
    try:
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
