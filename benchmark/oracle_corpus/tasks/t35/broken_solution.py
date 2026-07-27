def multisort(records, keys):
    for field, direction in keys:
        if direction not in ("asc", "desc"):
            raise ValueError("invalid direction: %r" % (direction,))

    indices = list(range(len(records)))
    # If the primary sort is descending, reverse the whole ordering.
    reverse = bool(keys) and keys[0][1] == "desc"

    def key_of(i):
        rec = records[i]
        # Build a composite key from the fields, using original index last so
        # equal records keep input order.
        return tuple(rec[field] for field, _ in keys) + (i,)

    indices.sort(key=key_of, reverse=reverse)
    return [records[i] for i in indices]
