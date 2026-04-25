[English](README.md) | [日本語](README.ja.md)

---

Prototype of a bot for the [Japanese Wiktionary](https://ja.wiktionary.org/wiki/Wiktionary:メインページ)

At the moment it only contains a series of string replacements that should applied by the bot.

The main transformation, implemented in `reading.py` updates to the `{{ja-noun}}` (and variants) template.

```diff
==={{noun}}===
-[[Category:{{ja}}_{{noun}}]]
-[[Category:{{ja}}_{{noun}}_サ変動詞]]
-{{jachar|思|慮}}（[[しりょ]]）
+{{ja-noun-suru|[[しりょ]]}}
```

Concretely, `main.py` contains a repl(acement) function that consumes wikitext, of signature:

```py
def repl(s: str) -> str:
    pass
```

Similarly, there are other replacement functions for some other fixes, but those are not prioritary.

---

### Usage

Install with `pip install .`

Tests are run with `pytest --verbose` (the verbose flag will show why some tests are skipped).

The project includes a CLI entry-point via `wb`. You can, for instance, run `wb run` to test the `repl` function against wikipages.

### TODO
- [ ] What is the difference between "ja-proper noun" [sample](https://ja.wiktionary.org/w/index.php?title=%E3%82%A2%E3%83%A0%E3%82%B9%E3%83%86%E3%83%AB%E3%83%80%E3%83%A0&action=edit) and "ja-name"

### Other suggestions
- An latin-alphabet version of [conj](https://ja.wiktionary.org/wiki/%E3%83%86%E3%83%B3%E3%83%97%E3%83%AC%E3%83%BC%E3%83%88:%E6%97%A5%E6%9C%AC%E8%AA%9E%E3%83%80%E6%B4%BB%E7%94%A8) and tag.
