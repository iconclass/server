# How to edit the Iconclass datafiles

In the light of the humanitarian catastrophe that is taking place in the Ukraine, it seems utterly trivial to discuss procedures for the maintenance and improvement of Iconclass. When war crimes are committed, when there is massive loss of life and countless people are bombed out of their homes, how relevant can it be to learn how to download your own copy of the datafiles of a _classification for cultural content_, how to edit its keywords and concept definitions, or how to enrich its content with new concepts?
If we now talk about the "_analysis of image metadata_", can we be referring to anything but the analysis of _EXIF information_ of [images, to check if they are manipulated and used for disinformation and propaganda purposes](https://www.bellingcat.com/tag/ukraine/){:target="read"}. We can't seriously be referring to the scholarly analysis of historical information about cultural artefacts? Or can we?
Also, wasn't Iconclass recently criticized for concepts that are discriminatory? Would that not mean that it represents an objectionable worldview and that efforts to improve it are a waste of time?

In such a vortex of events and emotions it would indeed be easy to question the relevance of a classification for the content of historical imagery. At the same time, however, today's images are the **source material for the study of history in the future**. So, no matter how modest their role may be, we should still try to forge the best possible tools for the documentation of image content.

It is against that background that we should first of all explain what we mean when we say that _Iconclass represents a view of the world_. A classification always reflects a certain bias because it organizes concepts in its own particular way. By describing the _raw data_ of our observations with the help of organized concepts, we transform those raw data into _information_. _Organizing concepts_ means that we _connect them_ in a certain way, we _assign them_ to categories which we then _subdivide_ hierarchically, following a chosen logic. Our choices are indeed the manifestation of a worldview, but in a more _technical sense_ than it may appear at first sight.

            {{% aimg ukraine %}}

For example, when a picture like this, of Ukraine's president Volodymyr Zelenskiy, is tagged with the following Iconclass concept:

- **54A81(+5) · Fearlessness, Intrepidity; 'Intrepidità & Costanza' (Ripa) (+ 'exemplum', representation of exemplary (historical) event)**

Iconclass expresses its particular view of the world first by subordinating the concept **54A81 · Fearlessness, Intrepidity ...** to the broader term **54A8 · Courage, Bravery, Valiance, Manliness ...** as shown in this screenshot of the chain of concepts:

{{% aimg 54A8 %}}

The relationship of these two concepts as broader and narrower term is not the only characteristic of the Iconclass worldview, however. The concept definition of **54A8** also puts **Courage** on a par with **Manliness**, which adds a "_male bias_" to the term.

            {{% aimg osipova %}}

If this image of the [arrest of Yelena Osipova](https://www.youtube.com/watch?v=otO0BI83FdI){:target="read"}, for protesting against the war, were tagged with the same concept **54A8 · Courage, Bravery, Valiance, Manliness ...**, it would be retrieved by a search for "_Manliness_". That would make the hit a "false positive", even if the behaviour of the policemen could be regarded as the manifestation of a certain type of manliness...
The decision to assign the concept of **Fearlessness** to these images, will ultimately depend on the interpretation of the historians who record and document (visual) sources for future generations. In the act of assigning this particular concept to the images, _their_ view of the world and _their_ interpretation of history will manifest itself.

The **male bias** of the concept definition, however, is an internal Iconclass issue; understandably, the mentality of sources like Cesare Ripa's _Iconologia_ trickled through in the Iconclass vocabulary. However, the words of the definitions are not carved in stone. They can be edited to adapt them to modern ideas, for instance about inclusivity and discrimination. Modernizing the definition to detach the concept of **Courage** from its male bias - by removing the word **manliness** - will obviously improve its applicability. Explaining how this can be done and how every member of the Iconclass user community can assist and act as a co-editor, is the main purpose of this page.

At the core of the editorial process are the **Iconclass data files**, which are stored in the [Open Access repository of **Github**](https://github.com/iconclass/data){:target="read"}.

{{% aimg github %}}

##### Register with GitHub and clone the data files

The first step to set yourself up as co-editor of Iconclass, is to register with GitHub and then **Clone** the data files from the repository, i.e. to download your own copy of the Iconclass files. The screenshot below shows the files and folders that will end up on your computer in a Windows _Explorer_ environment when you clone the repository.

{{% aimg wingit %}}

Those data files are simple [UTF-8](https://en.wikipedia.org/wiki/UTF-8){:target="read"} encoded, **structured text** files. They can be edited with any [plain text editor](https://en.wikipedia.org/wiki/Plain_text){:target="read"}.

The file that is named **notations.txt** can be regarded as the spine of the system. Every concept in Iconclass consists of a definition and an alphanumeric code - a **notation** - which assigns every definition its unique location in the schedules. The **notations.txt** file thus is a virtual roadmap of the entire Iconclass system. It contains all - almost 40,000 - unique notations, each one of which is the core of a record in the notations file that is structured like this (**field names** consist of a single capital letter):

**N** = [Notation](basics#notations){:target="read"} - the alphanumeric code
**K** = [Key](basics#keys){:target="read"} - if a list of keys is available for the concept, its identifier is entered in the **K** field
**C** = [Children](basics#path){:target="read"} - the logic of a classification is hierarchical subdivision; the subdivisions of a concept are its "_Children_"
**;** = repeated field - in the example there are four entries in the field **C**, preceded by a semi-colon and a space
**R** = [Reference](basics#cross){:target="cross"} - an (often associative) cross-reference to a related concept
**$** = End of record

A random example of a record with all of these elements:

        N 11A
        K 11k
        C 11A1
        ; 11A2
        ; 11A3
        ; 11A4
        R 11C
        $

When this record is imported in the Browser database, the [server software](https://github.com/iconclass/server){:target="read"} will transform the data into this piece of information by adding the corresponding definitions to the notations, fetching the list of **keys** and activating the hyperlinks:

[{{% aimg browser_11A %}}](/11A){:target="read"}
**Click the screenshot** to open the Browser and see the _sample images_ added too.

### Judensau, nazism, snake-charmer

{{% aimg add_icdata_001 %}}

The words and concepts we use to describe historical images are not neutral; language never is. The relationships we construct to connect those concepts and turn them into a classification system, are not objective; world views never are.
Maintaining a vocabulary for the description of historical images is therefore a balancing act by definition. Its essential purpose is to offer today's words for the description of images that document yesterday's ideas, tastes and mentality. Anachronism and subjectivity are thus unavoidable features of every metadata system, and Iconclass is no exception.

However, rather than _disqualifying_ controlled vocabularies, these features are an important reason to _use_ them. The reason is simple. Of necessity a classification system is transparent and unambiguous about its semantics because every concept is a link in a chain, every term a node of a branch.
You may _disagree_ with the construction of a branch, with the way concepts are defined and connected, but those connections are never hidden from view.

This section still needs to be written, but please [have a look at the data on Github](https://github.com/iconclass/data) as a good starting point.
