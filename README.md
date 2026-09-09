# Python repair demonstration: JSONL import fails on a blank line

This is an original, self-created demonstration. It contains synthetic data and is not a paid customer project.

## Reproduce the problem

The common implementation below throws `JSONDecodeError` on the empty line between the two records:

```python
import json
content = '{"id":1}\n\n{"id":2}\n'
records = [json.loads(line) for line in content.splitlines()]
```

The example fix skips blank lines, accepts an initial UTF-8 BOM, preserves record order and handles malformed records explicitly. It converts a JSONL file of objects to a JSON array.

## Run

Python 3.9 or later, standard library only:

```sh
python3 jsonl_to_json.py demo.jsonl result.json
python3 -m unittest -v test_converter.py
```

`result.json` must not already exist. Choose a new name for a second run.

## Acceptance checks

1. A BOM, blank lines, Chinese text and a large integer ID are handled correctly.
2. A `\n` escape inside a string stays inside the string.
3. A malformed record reports its physical line number, returns exit code 2 and creates no output file.
4. Existing output files retain their original contents whether input is valid or invalid.
5. Nonstandard numeric values such as `NaN` and non-object records are rejected.

## Scope and limits

Designed for small local UTF-8 files containing one object per nonblank line. It validates all input in memory before writing. It does not repair malformed JSON, stream large files, merge fields or accept arbitrary encodings. A disk failure during writing can leave a partial **new** file; an existing file is never replaced. Tested locally on the Python version recorded in `validation.txt`; other operating systems have not been tested.

The tests exercise the actual command-line script in separate processes.

## Small script repairs

For a similar reproducible Python issue, contact **takeiteasy@agent.qq.com** with sanitized code, the error, a minimal input, and the expected result. A $5 repair covers one agreed issue, corrected source, a regression test, and run instructions. Scope and delivery time are agreed before work starts.

This demonstration is free to inspect and reuse under the MIT license.
