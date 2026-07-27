def first_path_with_tag(tree, tag):
    def dfs(node, path):
        if tag in node["tags"]:
            return path + [node["id"]]
        for report in node["reports"]:
            result = dfs(report, path + [node["id"]])
            if result:
                return result
        return []

    return dfs(tree, [])