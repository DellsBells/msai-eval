from typing import List

def run_bin(capacity: int, events: List[tuple]) -> None:
    """
    Simulates the behavior of bins in a warehouse system.
    
    :param capacity: Maximum number of items that can be stored in each bin.
    :param events: A list where each element is a tuple representing an event (e.g., ('add', item), ('remove', item)).
                   'add' indicates adding an item to the bin, while 'remove' indicates removing an item from it.
    """
    bins = []
    
    def add_item(bin_index: int, item):
        if len(bins[bin_index]) < capacity:
            bins[bin_index].append(item)
    
    def remove_item(bin_index: int, item):
        try:
            bins[bin_index].remove(item)
        except ValueError:
            pass  # Item not found in bin
    
    for event_type, item in events:
        if event_type == 'add':
            add_item(0, item)  # Assuming only one bin is used
        elif event_type == 'remove':
            remove_item(0, item)  # Assuming only one bin is used

# Example usage
events = [('add', 'apple'), ('add', 'banana'), ('remove', 'banana')]
run_bin(2, events)
print(bins[0])  # Output should be ['apple']