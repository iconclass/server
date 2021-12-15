# Linked Open Data

ICONCLASS has been available as a SKOS dataset on the web since 2015.
For this new version we plan on continuing that support, and adding new features like a SPARQL endpoint.

Every notation in ICONCLASS is associated with a Uniform Resource Identifier (URI) that is unique to that subject heading. For example the concept "Communication of Thought" has a notation of 52D1 and thus the URI becomes: http://iconclass.org/52D1. If you click on the aforementioned link, you are redirected to a HTML representation of that concept, fit for human consumption.

It is also possible to retrieve machine-readable formats, by either appending '.rdf' or '.json' to the URI. This will redirect you to either a [SKOS/RDF](https://www.w3.org/2004/02/skos/) or JSON representation of the concept. For example [http://iconclass.org/52D1.rdf](/52D1.rdf) or [http://iconclass.org/52D1.jsonld](/52D1.jsonld) or even [http://iconclass.org/52D1.json as simpler JSON](/52D1.json)

If you need to retrieve the data for notations containing 'keys' like a 25F23(+46) sleeping animal(s) ensure that you properly encode the + sign in the URL. The link becomes: http://iconclass.org/25F23(LION)(%2B46).json. Note how the + sign has been replaced with the characters %2B For more information have a look at the [Wikipedia article for Percent Encoding](https://en.wikipedia.org/wiki/Percent-encoding). You have to do the same for names, like: 11H(BASIL THE GREAT).
