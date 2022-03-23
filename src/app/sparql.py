from rdflib.plugins.sparql.evaluate import evalBGP
from rdflib.plugins.sparql.sparql import AlreadyBound
from rdflib.plugins.sparql import CUSTOM_EVALS
from rdflib.plugins.sparql.results.jsonresults import JSONResultSerializer
from rdflib import Graph, URIRef, Variable
from fastapi.responses import JSONResponse
from urllib.parse import quote
from io import StringIO
import json
from .main import app
from .util import do_search


SPARQL_FTS = URIRef("http://iconclass.org/search")
SPARQL_FTS_NOKEYS = URIRef("http://iconclass.org/searchnokeys")


def getq(ctx, vars):
    for var, qtipe, val in vars:
        lang = val.language or "en"
        lang = lang[:2]
        if lang not in ("en", "de"):
            lang = "en"  # at the moment we only allow searching in English and German. There are only so many hours in the day
        sort = "rank"
        val = str(val)

        search_results = do_search(
            q=val, r="", lang=lang, sort=sort, keys=(qtipe == SPARQL_FTS)
        )

        for notation in search_results:
            c = ctx.push()
            try:
                c[var] = URIRef("http://iconclass.org/" + quote(notation))
            except AlreadyBound:
                continue

            yield c.solution()


def fts_eval(ctx, part):
    if part.name != "BGP":
        raise NotImplementedError()
    vars = []
    for t in part.triples:
        if not isinstance(t[0], Variable):
            continue
        if t[1] in (SPARQL_FTS, SPARQL_FTS_NOKEYS):
            vars.append(t)
    if len(vars) > 0:
        return getq(ctx, vars)
    return evalBGP(ctx, part)


@app.get(
    "/sparqlfts",
)
def sparqlfts(query: str):
    result = g.query(query)

    ser = JSONResultSerializer(result)
    buf = StringIO()
    ser.serialize(buf)

    return JSONResponse(json.loads(buf.getvalue()))


CUSTOM_EVALS["fts_eval"] = fts_eval
g = Graph()


if __name__ == "__main__":
    for x in g.query(
        """
        SELECT ?s
        WHERE {
            ?s <http://iconclass.org/fts> "fish" .
        }
        """
    ):
        print(x)
