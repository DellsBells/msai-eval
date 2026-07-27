def order_roster(employees):
    # Python's sort is stable, so equal keys preserve input order (rule 4).
    # Key: dept ascending, salary descending (negate), name ascending.
    return sorted(
        employees,
        key=lambda e: (e["dept"], -e["salary"], e["name"]),
    )
