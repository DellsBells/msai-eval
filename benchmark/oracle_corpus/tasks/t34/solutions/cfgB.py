def rank_contestants(contestants):
    # Sort contestants by score in descending order,
    # then by penalty in ascending order.
    sorted_contestants = sorted(contestants, key=lambda x: (-x['score'], x['penalty']))
    
    return [contestant['id'] for contestant in sorted_contestants]