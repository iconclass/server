# On SKOS & SPARQL

The base Iconclass vocabularly has been available as Linked Open Data since 2011. This meant that each notation on the site
could also be viewed as RDF in either RDX-XML or as a simple JSON view by appending `.rdf` or `.json` behind the URI for a notation.
[For example 71F2172](http://iconclass.org/71F2172.rdf)

This was done in the Python server software to convert the data for a notation dynamically per-request. There was not a "dump" of the
underlying data in a database that showed snippets, but the [relatively complex data structure](https://github.com/iconclass/data)
was being processed and served.

There is a large difference between the "base" number of notations, and the number of notations including "keys"

What are these "keys"? It is essentially mini sub-trees that can be switched on and off at various point in the main hierarchy.
It adds extra digits between brackets, prefixed with a plus sign. For example, at the item [11R1 personifications ~ the life of man](/11R1.json) note the _children_ at this point in the tree:

```json
["11R1(+0)", "11R1(+1)", "11R1(+2)", "11R1(+3)", "11R1(+4)", "11R1(+5)"]
```

When we for example add the digit (+1) to the notation it becomes [personifications ~ the life of man (+ Holy Trinity)](/11R1%28+1%29.json)
But when we look at some other part in the tree, and we add the digit (+1) the text is modified in a different way, for example, at various places these are the extra items that are added:

| notation | text added with a (+1)                         |
| -------- | ---------------------------------------------- |
| 11R1     | (+ Holy Trinity)                               |
| 25F      | (+ animals used symbolically)                  |
| 25FF     | (+ parts, limbs and organs larger than normal) |

...and the list is [actually quite a bit longer](https://github.com/iconclass/data/blob/main/keys.txt):

### List of key sub-trees

| ID      | count of branches |
| ------- | ----------------- |
| 11k     | 14                |
| 12k     | 1                 |
| 23k     | 61                |
| 25D11k  | 3                 |
| 25D3k   | 8                 |
| 25FFk   | 334               |
| 25FFkq  | 18                |
| 25Fk    | 204               |
| 25Gk    | 39                |
| 25Hk    | 2                 |
| 25Ik    | 2                 |
| 25Kk    | 2                 |
| 25Lk    | 2                 |
| 2k      | 1                 |
| 31A42k  | 151               |
| 31A42kq | 24                |
| 31A44k  | 151               |
| 31A44kq | 24                |
| 31A45k  | 13                |
| 31A54k  | 4                 |
| 31E23k  | 24                |
| 31F2k   | 7                 |
| 31k     | 116               |
| 32Bk    | 12                |
| 34k     | 241               |
| 3k      | 1                 |
| 41B3k   | 4                 |
| 41Cm    | 12                |
| 41Cn    | 11                |
| 41Dk    | 26                |
| 41k     | 8                 |
| 43Ak    | 18                |
| 43B3k   | 11                |
| 43C1k   | 71                |
| 43Ck    | 33                |
| 44Ak    | 13                |
| 44Gk    | 55                |
| 45k     | 61                |
| 46Ck    | 274               |
| 47k     | 353               |
| 48A98k  | 112               |
| 48k     | 174               |
| 49Bk    | 21                |
| 49k     | 37                |
| 4k      | 1                 |
| 5k      | 39                |
| 5kq     | 6                 |
| 61Ak    | 5                 |
| 61Bk    | 24                |
| 6k      | 1                 |
| 7k      | 14                |
| 8k      | 1                 |
| 91k     | 15                |
| 92k     | 15                |
| 93k     | 15                |
| 96Ak    | 15                |
| 98k     | 24                |
| 9k      | 1                 |

So when we expand the tree by adding these keys, the counts look like this:

|                    | Count     |
| ------------------ | --------- |
| Base Notations     | 39,956    |
| All including keys | 1,346,423 |

A significant increase. But many of these extensions are fairly "dumb" - in the sense that it only takes the base notations and add some repetitive modifier texts. So there is huge amount of redundancy in these additional nodes. Can't we just leave them out?
This is tempting to do. Certain services, [like here](http://finto.fi/ic/en/), do that, as it means the dataset is much smaller. To be fair, that was also the download available on the Iconclass website, but expressly saying that the crucial "keys" part is missing, as it makes the data mushroom to quite large sizes.

_What do you miss when you leave out the keys?_
My favourite examples are these, compare the results for: [lion sleeping](/en/_?q=lion%20sleeping) and [lion sleeping](/en/_?q=lion%20sleeping&k=1)
In the first case we do not add the keys, and miss out on the important - more relevant exact notation for that concept: [/25F23%28LION%29%28+46%29.json]()

To not even mentioned that these notations with keys have been used in various databases all over the world in both analog and digital forms over the last 50 years, and we can not magically wave a wand and make them disappear. (even though as a software developer I have often cursed and wished this were the case 😅 )

And now back to the SKOS/SPARQL question:

### Do we dump & load the entire tree, including keys, in a triplestore? (despite redundancy)

Or do we devise some form of expressing these "keys" as extra items in the SKOS representation, and place the onus on knowledgebase users to construct the textual labels including the extra key texts by themselves?

...and typing out the question and explanation like this almost answers the question by itsself.
