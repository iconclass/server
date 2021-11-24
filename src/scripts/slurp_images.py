# Read in a dmp file from command line, and import into the images index
import textbase, sqlite3, sys

i, u = [], []
for x in textbase.parse(sys.argv[1]):
    try:
        ics = [(x["ID"][0], ic) for ic in x.get("IC", [])]
        if len(ics) < 1:
            continue
        u.extend(ics)
        i.append(
            (x["ID"][0], x["URL.IMAGE"][0], x["URL.WEBPAGE"][0], x["CAPTION.EN"][0])
        )
    except KeyError:
        continue

d = sqlite3.connect("iconclass.sqlite")
c = d.cursor()
c.executemany("INSERT INTO images VALUES (?, ?, ?, ?)", i)
c.executemany("INSERT INTO images_ic VALUES (?, ?)", u)
d.commit()
