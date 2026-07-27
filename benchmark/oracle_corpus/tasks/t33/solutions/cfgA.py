def order_roster(employees):
    from functools import cmp_to_key

    def compare(emp1, emp2):
        if emp1['dept'] != emp2['dept']:
            return (emp1['dept'] > emp2['dept']) - (emp1['dept'] < emp2['dept'])
        if emp1['salary'] != emp2['salary']:
            return (emp2['salary'] > emp1['salary']) - (emp2['salary'] < emp1['salary'])
        if emp1['name'] != emp2['name']:
            return (emp1['name'] > emp2['name']) - (emp1['name'] < emp2['name'])
        return 0

    return sorted(employees, key=cmp_to_key(compare))