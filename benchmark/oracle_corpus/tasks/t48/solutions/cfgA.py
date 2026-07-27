def query(data, pattern):
    def pre_order_traversal(node, visit_fn):
        if isinstance(node, dict):
            for key in node:
                visit_fn(node[key])
                pre_order_traversal(node[key], visit_fn)
        elif isinstance(node, list):
            for item in node:
                visit_fn(item)
                pre_order_traversal(item, visit_fn)

    def match_step(nodes, step):
        result = set()
        
        if step == "*":
            for node in nodes:
                if isinstance(node, dict):
                    result.update(node.values())
                elif isinstance(node, list):
                    result.update(node)
        elif step == "**":
            seen = set()
            for node in nodes:
                pre_order_traversal(node, lambda x: (seen.add(x) or result.add(x)) if x not in seen else None)
        elif isinstance(step, int):
            for node in nodes:
                if isinstance(node, list) and 0 <= step < len(node):
                    result.add(node[step])
        elif isinstance(step, str):
            for node in nodes:
                if isinstance(node, dict) and step in node:
                    result.add(node[step])
        
        return result

    current_nodes = {data}
    
    for step in pattern:
        current_nodes = match_step(current_nodes, step)
    
    return list(current_nodes)

# Example usage:
# data = {"a": {"b": [10, 20, 30]}}
# print(query(data, ["a", "b", 1]))  # -> [20]