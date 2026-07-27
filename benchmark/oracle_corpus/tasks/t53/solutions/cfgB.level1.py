def simulate_elevator(start_floor, requests, min_floor, max_floor):
    """
    Simulates an elevator trip based on the start floor,
    list of requested floors, minimum and maximum allowed floors.

    :param start_floor: Starting floor of the elevator.
    :type start_floor: int
    :param requests: List of floors where the elevator stops to pick up or drop off passengers.
    :type requests: list[int]
    :param min_floor: The lowest floor that can be reached by the elevator.
    :type min_floor: int
    :param max_floor: The highest floor that can be reached by the elevator.
    :type max_floor: int
    :return: A string describing the elevator trip, starting with "Elevator starts at floor" followed by start_floor,
             and ending with a description of its final position after servicing all requests in order.
    :rtype: str
    """
    current_floor = start_floor
    direction = 1 if min_floor <= start_floor < max_floor else -1
    
    trip_log = f"Elevator starts at floor {current_floor}"
    
    for request in sorted(requests):
        while current_floor != request:
            if current_floor < request and direction == 1 or (current_floor > request and direction == -1):
                current_floor += direction
                trip_log += f", goes up to floor {current_floor}" if direction == 1 else f", goes down to floor {current_floor}"
            elif current_floor != min_floor and direction * (min_floor - max_floor) < 0:
                current_floor = min_floor if current_floor > min_floor else max_floor
                trip_log += f", stops at floor {current_floor}" if request == current_floor else ""
    
    return trip_log + f". Final position: floor {current_floor}"

# Example usage:
print(simulate_elevator(3, [6, 2, 5], 1, 8))