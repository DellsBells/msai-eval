# Undo/Redo Command Log

You are building the history engine for a small text buffer. The buffer holds a
single Python string, starting empty (`""`). Callers drive it with a list of
command tokens; you replay the whole log and return the buffer's final contents.

Implement a single function:

```python
def run_editor(commands: list[str]) -> str:
    ...
```

`commands` is a list of strings. Each string is one command. Process them strictly
in order, maintaining the buffer plus an **undo stack** and a **redo stack**.

## Commands

There are exactly four command forms:

1. `"APPEND:<text>"` — append `<text>` (everything after the first colon) to the
   end of the buffer. `<text>` may be empty and may itself contain colons; only the
   **first** colon separates the verb from the payload. This is an *editing*
   command.

2. `"BACKSPACE:<n>"` — remove the last `<n>` characters from the buffer, where
   `<n>` is a base-10 non-negative integer. If `<n>` is greater than or equal to
   the current buffer length, the buffer becomes empty (`""`). This is an *editing*
   command.

3. `"UNDO"` — revert the most recent editing command that has not already been
   undone. Concretely: pop the top entry of the undo stack, restore the buffer to
   the state saved in that entry, and push the entry onto the redo stack. If the
   undo stack is empty, `UNDO` does nothing at all (the buffer is unchanged and the
   stacks are unchanged).

4. `"REDO"` — re-apply the most recently undone editing command. Concretely: pop
   the top entry of the redo stack, restore the buffer to the state saved in that
   entry, and push the entry onto the undo stack. If the redo stack is empty,
   `REDO` does nothing at all.

## State-machine rules (read carefully)

- Before an **editing** command (`APPEND` or `BACKSPACE`) mutates the buffer, push
  an entry recording the buffer contents **as they were just before** this edit
  onto the **undo stack**. Then apply the edit.

- Executing any **editing** command **clears the redo stack** — once you type new
  text, previously-undone edits can no longer be redone.

- `UNDO` and `BACKSPACE` are different: `UNDO` moves an entry between the two
  stacks and restores a saved snapshot; `BACKSPACE` is itself an edit that gets
  recorded for later undoing.

- `UNDO` restores the buffer to the snapshot saved *before* the undone edit. The
  redo entry must remember the buffer state that `UNDO` replaced, so that a later
  `REDO` restores it exactly.

- `UNDO`/`REDO` when their stack is empty are silent no-ops and must **not** clear
  the other stack.

You may assume every command string is well-formed according to the forms above.

## Return value

Return the final buffer string after all commands are processed.

## Examples

```python
run_editor(["APPEND:hello", "APPEND: world"])
# -> "hello world"

run_editor(["APPEND:abc", "BACKSPACE:2", "UNDO"])
# APPEND -> "abc"; BACKSPACE:2 -> "a"; UNDO reverts backspace -> "abc"
# -> "abc"

run_editor(["APPEND:a", "APPEND:b", "UNDO", "REDO"])
# "a" then "ab"; UNDO -> "a"; REDO -> "ab"
# -> "ab"

run_editor(["APPEND:x", "UNDO", "APPEND:y", "REDO"])
# "x"; UNDO -> ""; APPEND:y -> "y" (this edit clears redo);
# REDO now has nothing to redo -> stays "y"
# -> "y"

run_editor(["UNDO", "REDO", "APPEND:hi:there"])
# leading UNDO/REDO are no-ops; only first colon splits -> payload "hi:there"
# -> "hi:there"
```
