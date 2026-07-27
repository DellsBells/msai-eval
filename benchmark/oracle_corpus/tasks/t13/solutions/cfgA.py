from datetime import date, timedelta

def working_days(start: str, end: str, holidays: list[str]) -> int:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    holiday_set = set(date.fromisoformat(day) for day in holidays)
    
    if start_date > end_date:
        return 0
    
    count = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5 and current_date not in holiday_set:
            count += 1
        current_date += timedelta(days=1)
    
    return count