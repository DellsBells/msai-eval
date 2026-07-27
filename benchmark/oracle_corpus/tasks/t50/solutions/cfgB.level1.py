def longest_shared_run(a: str, b: str) -> tuple[int, int]:
    def shared_run_length(s: str):
        if not s:
            return 0
        count = max_len = 1
        for i in range(1, len(s)):
            if s[i] == s[i-1]:
                count += 1
                max_len = max(max_len, count)
            else:
                count = 1
        return max_len

    a_run_length = shared_run_length(a)
    b_run_length = shared_run_length(b)

    return (a_run_length, b_run_length)