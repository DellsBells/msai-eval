def order_roster(employees):
    # Sort by department, then salary, then name.
    return sorted(
        employees,
        key=lambda e: (e["dept"], e["salary"], e["name"]),
    )
