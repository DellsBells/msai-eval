def simulate_elevator(start_floor, requests, min_floor, max_floor):
    current = start_floor
    distance = 0
    stops = 0
    for req in requests:
        if req < min_floor or req > max_floor:
            continue
        distance += abs(req - current)
        current = req
        stops += 1
    return {"final_floor": current, "distance": distance, "stops": stops}
