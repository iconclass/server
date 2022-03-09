# How to edit the Iconclass datafiles

In the light of the humanitarian catastrophe that is taking place in the Ukraine, it seems utterly trivial to discuss procedures for the maintenance and improvement of Iconclass. When war crimes are committed, when there is massive loss of life and countless people are bombed out of their homes, how relevant can it be to learn how to download your own copy of the datafiles of a _classification for cultural content_, how to edit its keywords and concept definitions, or how to enrich its content with new concepts?
If we now talk about the "_analysis of image metadata_", can we be referring to anything but the analysis of _EXIF information_ of [images, to check if they are manipulated and used for disinformation and propaganda purposes](https://www.bellingcat.com/tag/ukraine/){:target="read"}. We can't seriously be referring to the scholarly analysis of historical information about cultural artefacts? Or can we?
Also, wasn't Iconclass recently criticized for concepts that are discriminatory? Would that not mean that it represents an objectionable worldview and that efforts to improve it are a waste of time?

In such a vortex of events and emotions it would indeed be easy to question the relevance of a classification for the content of historical imagery. At the same time, however, today's images are the __source material for the study of history in the future__. So, no matter how modest their role may be, we should still try to forge the best possible tools for the documentation of image content.

It is against that background that we should first of all explain what we mean when we say that _Iconclass represents a view of the world_. A classification always reflects a certain bias because it organizes concepts in its own particular way. By describing the _raw data_ of our observations with the help of organized concepts, we transform those raw data into _information_. _Organizing concepts_ means that we _connect them_ in a certain way, we _assign them_ to categories which we then _subdivide_ hierarchically, following a chosen logic. Our choices are indeed the manifestation of a worldview, but in a more _technical sense_ than it may appear at first sight.

            {{% aimg ukraine %}}

For example, when a picture like this, of Ukraine's president Volodymyr Zelenskiy, is tagged with the following Iconclass concept:

* __54A81(+5) · Fearlessness, Intrepidity; 'Intrepidità & Costanza' (Ripa) (+ 'exemplum', representation of exemplary (historical) event)__

Iconclass expresses its particular view of the world first by subordinating the concept __54A81 · Fearlessness, Intrepidity ...__ to the broader term __54A8 · Courage, Bravery, Valiance, Manliness ...__ as shown in this screenshot of the chain of concepts:

{{% aimg 54A8 %}}

The relationship of these two concepts as broader and narrower term is not the only characteristic of the Iconclass worldview, however. The concept definition of __54A8__ also puts __Courage__ on a par with __Manliness__, which adds a "_male bias_" to the term. 

            {{% aimg osipova %}}

If this image of the [arrest of Yelena Osipova](https://www.youtube.com/watch?v=otO0BI83FdI){:target="read"}, for protesting against the war, were tagged with the same concept __54A8 · Courage, Bravery, Valiance, Manliness ...__, it would be retrieved by a search for "_Manliness_". That would make the hit a "false positive", even if the behaviour of the policemen could be regarded as the manifestation of a certain type of manliness...
The decision to assign the concept of __Fearlessness__ to these images, will ultimately depend on the interpretation of the historians who record and document (visual) sources for future generations. In the act of assigning this particular concept to the images, _their_ view of the world and _their_ interpretation of history will manifest itself.

The __male bias__ of the concept definition, however, is an internal Iconclass issue; understandably, the mentality of sources like Cesare Ripa's _Iconologia_ trickled through in the Iconclass vocabulary. However, the words of the definitions are not carved in stone. They can be edited to adapt them to modern ideas, for instance about inclusivity and discrimination. Modernizing the definition to detach the concept of __Courage__ from its male bias - by removing the word __manliness__ - will obviously improve its applicability. Explaining how this can be done and how every member of the Iconclass user community can assist and act as a co-editor, is the main purpose of this page.

At the core of the editorial process are the __Iconclass data files__, which are stored in the [Open Access repository of __Github__](https://github.com/iconclass/data){:target="_read"}.

{{% aimg github %}}

##### Register with GitHub and clone the data files

The first step to set yourself up as co-editor of Iconclass, is to register with GitHub and then __Clone__ the data files from the repository, i.e. to download your own copy of the Iconclass files. The screenshot below shows the files and folders that will end up on your computer in a Windows _Explorer_ environment when you clone the repository.

{{% aimg wingit %}}

Those data files are simple [UTF-8](https://en.wikipedia.org/wiki/UTF-8){:target="_read"} encoded, __structured text__ files. They can be edited with any [plain text editor](https://en.wikipedia.org/wiki/Plain_text){:target="_read"}.

The file that is named __notations.txt__ can be regarded as the spine of the system. Every concept in Iconclass consists of a definition and an alphanumeric code - a __notation__ - which assigns every definition its unique location in the schedules. The __notations.txt__ file is a virtual roadmap of the entire Iconclass system. It contains all - almost 40,000 - unique notations, each one of which is the core of a record in the text file that starts with a capital __N__ and ends with __$__. A typical record looks like this:

        N 11A
        K 11k
        C 11A1
        ; 11A2
        ; 11A3
        ; 11A4
        R 11C
        $

The structure of a records is simple. These are the main elements (__field names__ consist of a single capital letter):

__N__ = Notation - the alphanumeric code
__K__ = Key - if a list of keys is available for the concept, its identifier is entered in the __K__ field
__C__ = Children - the logic of a classification is subdivision; the subdivisions of a concept are its "_Children_"
__;__ = repeated field - in the example there are four entries in the field __C__, preceded by a semi-colon and a space
__R__ = Reference - an (often associative) cross-reference to a related concept
__$__ = End of record

When this record is imported in the Browser database, the [server software](https://github.com/iconclass/server){:target="_read"} will transform the data into this piece of information:

{{% aimg browser_11A %}}

The notations are supplemented by the texts of the concept definitions, the keywords . The cross reference



### Judensau, nazism, snake-charmer

{{% aimg add_icdata_001 %}}


The words and concepts we use to describe historical images are not neutral; language never is. The relationships we construct to connect those concepts and turn them into a classification system, are not objective; world views never are.
Maintaining a vocabulary for the description of historical images is therefore a balancing act by definition. Its essential purpose is to offer today's words for the description of images that document yesterday's ideas, tastes and mentality. Anachronism and subjectivity are thus unavoidable features of every metadata system, and Iconclass is no exception.

However, rather than _disqualifying_ controlled vocabularies, these features are an important reason to _use_ them. The reason is simple. Of necessity a classification system is transparent and unambiguous about its semantics because every concept is a link in a chain, every term a node of a branch. 
You may _disagree_ with the construction of a branch, with the way concepts are defined and connected, but those connections are never hidden from view. 


This section still needs to be written, but please [have a look at the data on Github](https://github.com/iconclass/data) as a good starting point.

