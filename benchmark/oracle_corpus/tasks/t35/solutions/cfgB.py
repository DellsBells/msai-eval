def multisort(records, keys):
    def key_func(record):
        for key, direction in keys:
            if key not in record or key not in ["asc", "desc"]:
                raise ValueError(f"Invalid sort key: {key}")
            yield (record[key], -1) if direction == "desc" else (record[key], 1)
    return sorted(records, key=key_func)

# Example usage
recs = [
    {"team": "B", "wins": 3, "name": "y"},
    {"team": "A", "wins": 5, "name": "x"},
    {"team": "A", "wins": 5, "name": "w"}
]
sorted_records = multisort(recs, [("team", "asc"), ("wins", "desc")])
print(sorted_records)