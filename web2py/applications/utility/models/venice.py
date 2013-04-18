# Everything will be finalized into the db when you run this:
def random_prisoner():
    return db().select(db.prisoners.ALL,orderby='<random>',limitby=(0,1))[0]

def shuffle_names():
    # For each row
    for row in db.prisoners.all():
        # Remember the original name for this row
        tmp_message = row.name

        # Get a random row
        random_row = random_prisoner()

        # Now swap their names
        row.update_record(name=random_row.name)
        random_row.update_record(name=row.name)

#db.commit()
