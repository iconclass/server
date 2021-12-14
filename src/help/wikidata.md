# ICONCLASS and WikiData

Here is an example query of items that have been described on Wikidata with ICONCLASS

<iframe style="width: 100%" src="https://query.wikidata.org/embed.html#%23defaultView%3AImageGrid%0A%23%20Images%20described%20using%20ICONCLASS%0ASELECT%20DISTINCT%20%3Fitem%20%3FitemLabel%20%3Fpic%0AWHERE%0A%7B%0A%3Fitem%20wdt%3AP1257%20%3Ffoo%20.%0A%3Fitem%20wdt%3AP18%20%3Fpic%0ASERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22%20%7D%0A%7D%20ORDER%20BY%20%3FitemLabel" />
