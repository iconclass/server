# SPARQL Support

We are finally getting round to adding [SPARQL](https://en.wikipedia.org/wiki/SPARQL) support to ICONCLASS. This means that there is a special URL: [/sparql](/sparql) that can be called to perform semantic web queries.

What is this useful for? As a start, there is a need to add support for ICONCLASS to the Dutch [Termennetwerk](https://termennetwerk.netwerkdigitaalerfgoed.nl/) - a search engine for terminologies. The Termennetwerk functions by doing a query of multiple terminology sources that present their content via SPARQL, and then presents the results as a uniform output. The output of the service can then be linked to collection management systems at cultural heritage institutions.

But this is not the only application for which a SPARQL endpoint is useful. It can also be queried directly by other applications. It is then possible to do more advanced queries that are not bound by the interface of a particular software application.

### Development notes

The very first version used Blazegraph as the triplestore. It is fast, easy to install and widely used. But alas, it os also
