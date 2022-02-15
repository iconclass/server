
# in data we expect objects with "caption", "id"
def to_metabotnik(db_filename, project_name, json_filename, data):
    mapping = json.load(open(json_filename))
    width, height = mapping['width'], mapping['height']

    data[filename]




    seqs = {}
    for seq, filename, caption, lemma in images:
        if filename not in image_paths:
            continue
        # seq looks like 3 numbers split with underscores, volume_column_seq, eg. 2_155_999
        seq = seq.split("_")
        if len(seq) != 3:
            continue
        seqs[image_paths[filename]] = ("_".join(seq), f"{seq[0]}_{seq[1]}\n{lemma}\n{caption}")


    insert_objs = []  # the object data in json we want to serve up
    insert_xy = []    # these are the coordinates, mapped to a numeric id
    insert_tags = []   # tags maps object ids to numeric ids
    count = 1
    for obj in mapping["images"]:
        if obj["filename"] not in data:
            continue
        obj_data = data[obj["filename"]]
        obj_id = obj_data.get("id")
        if not obj_id:
            continue
        insert_objs.append((count, obj_data))
        obj_seq = seqs[obj["filename"]][0]
        insert_tags.append((obj_id, count))
        # NOTE: in rtree we do not insert x y w h, but x1 x2, y1, y2 !!!!
        insert_xy.append((count, obj["x"]/width, obj["x"]/width + obj["width"]/width, obj["y"]/height, obj["y"]/height+obj["height"]/height))
        count += 1
        if count > 999999:
            break
    db = sqlite3.connect(db_filename)
    cursor = db.cursor()
    cursor.execute("INSERT INTO projects VALUES (?, ?, ?)", (project_name, width, height))
    cursor.execute(f"CREATE TABLE {project_name}_tags (tag, obj_id)")    
    cursor.execute(f"CREATE TABLE {project_name}_objs (id INTEGER PRIMARY KEY AUTOINCREMENT, obj)")
    cursor.execute(f"CREATE VIRTUAL TABLE {project_name}_index USING rtree(id, x1, x2, y1, y2)")
    cursor.executemany(f"INSERT INTO {project_name}_objs VALUES (?, ?)", insert_objs)
    cursor.executemany(f"INSERT INTO {project_name}_index VALUES (?, ?, ?, ?, ?)", insert_xy)
    cursor.executemany(f"INSERT INTO {project_name}_tags VALUES (?, ?)", insert_tags)
    db.commit()

