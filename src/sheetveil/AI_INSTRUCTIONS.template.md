# Instructions for the AI reviewing this workbook pair

You are given two locally tokenized Excel workbooks:

- `masked_before.xlsx`: the original workflow input
- `masked_after.xlsx`: the manually produced expected output

Each nonblank constant is replaced with a deterministic HMAC token. The same original value has the same token in both workbooks. Infer movement, copying, filtering, ordering, deletion, duplication, and layout changes from matching tokens and workbook structure. Tokens are opaque: do not attempt to infer original values.

Important limitations:

- A new token in the output may be newly entered or derived.
- Hardcoded arithmetic, substring extraction, concatenation, date arithmetic, and other derived values cannot be inferred from token identity alone.
- Preserved formulas are genuine workflow evidence and should be considered.
- Formatting, merged cells, dimensions, tables, and sheet layout may also describe the intended workflow.

Produce a clear transformation specification first. Only then generate automation. Do not hard-code sample tokens into the final solution; refer to source locations, headers, formulas, or structural rules.
