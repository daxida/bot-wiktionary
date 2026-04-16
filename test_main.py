import pytest

from main import repl_ja_template


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_ja_template(raw)
    assert expected == received, received


def test_repl_ja_noun_suru() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
[[Category:{{ja}}_{{noun}}_サ変動詞]]
{{jachar|思|慮}}（[[しりょ]]）
"""
    expected = """
==={{noun}}===
{{ja-noun-suru|[[しりょ]]}}
"""
    mktest(raw, expected)


def test_repl_ja_jachar1() -> None:
    raw = """
=={{ja}}==
[[Category:{{ja}}]]
{{kana-DEFAULTSORT|まつび}}
==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
{{jachar|末|尾}}（まつび）
#[[文章]]、[[数字]]、[[列]]など、ひと続きになっているものの{{ふりがな|末|すえ}}。[[おわり|終わり]]。[[最後]]。
"""
    expected = """
=={{ja}}==
[[Category:{{ja}}]]
{{kana-DEFAULTSORT|まつび}}
==={{noun}}===
{{ja-noun|まつび}}
#[[文章]]、[[数字]]、[[列]]など、ひと続きになっているものの{{ふりがな|末|すえ}}。[[おわり|終わり]]。[[最後]]。
"""
    mktest(raw, expected)


def test_repl_ja_jachar2() -> None:
    raw = """
=={{ja}}==
[[Category:{{ja}}]]
{{kana-DEFAULTSORT|とっきょ}}
==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
{{jachar|特|許}}（とっきょ）
#[[特定]]の人のために[[あたらしい|新しく]][[権利]]を[[設定]]すること。
#新しく[[考案]]された[[発明]]について、考案者に[[独占]]的、[[排他]]的に[[利用]]することを[[みとめる|認める]]こと。
===={{rel}}====
*[[特許権]]
    """
    expected = """
=={{ja}}==
[[Category:{{ja}}]]
{{kana-DEFAULTSORT|とっきょ}}
==={{noun}}===
{{ja-noun|とっきょ}}
#[[特定]]の人のために[[あたらしい|新しく]][[権利]]を[[設定]]すること。
#新しく[[考案]]された[[発明]]について、考案者に[[独占]]的、[[排他]]的に[[利用]]することを[[みとめる|認める]]こと。
===={{rel}}====
*[[特許権]]
"""
    mktest(raw, expected)


def test_repl_ja_jachars() -> None:
    raw = """
{{DEFAULTSORT:さいしゆう さいしゅう 最終}}
=={{ja}}==
[[Category:{{ja}}]]
==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
{{jachars}}（さいしゅう）
#[[一番]]の[[おわり|終わり]]。
===={{pron|jpn}}====
;さ↗いしゅー
    """
    expected = """
{{DEFAULTSORT:さいしゆう さいしゅう 最終}}
=={{ja}}==
[[Category:{{ja}}]]
==={{noun}}===
{{ja-noun|さいしゅう}}
#[[一番]]の[[おわり|終わり]]。
===={{pron|jpn}}====
;さ↗いしゅー
"""
    mktest(raw, expected)


def test_repl_ja_jachars_with_inner_category() -> None:
    raw = """
==={{noun}}===
[[カテゴリ:{{ja}}_{{noun}}]]
[[カテゴリ:妖怪]]
{{jachars}}（あかてこ）
#[[青森県]]八戸市に古くから伝わる[[妖怪]]。
"""
    expected = """
==={{noun}}===
{{ja-noun|あかてこ}}
[[カテゴリ:妖怪]]
#[[青森県]]八戸市に古くから伝わる[[妖怪]]。
"""
    mktest(raw, expected)


def test_repl_ja_bold_base() -> None:
    raw = """
=={{ja}}==
[[Category:{{ja}}|れんしよう れんじょう]]
==={{noun}}===
[[Category:{{ja}}_{{noun}}|れんしよう れんじょう]]
'''[[恋]] [[情]]'''（[[れんじょう]]）
#特定の[[ひと|人]]を[[こいしたう|恋い慕う]][[きもち|気持ち]]。
"""
    expected = """
=={{ja}}==
[[Category:{{ja}}|れんしよう れんじょう]]
==={{noun}}===
{{ja-noun|[[れんじょう]]}}
#特定の[[ひと|人]]を[[こいしたう|恋い慕う]][[きもち|気持ち]]。
"""
    mktest(raw, expected)


def test_repl_ja_bold_two_readings() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
'''[[哀]] [[音]]'''（あいおん, あいね）
# [[かなしい|悲しげ]]な[[こえ|声]]や[[おと|音]]。
"""
    expected = """
==={{noun}}===
{{ja-noun|あいおん|あいね}}
# [[かなしい|悲しげ]]な[[こえ|声]]や[[おと|音]]。
"""
    mktest(raw, expected)


def test_repl_ja_bold_long() -> None:
    raw = """
{{wikipedia}}
=={{ja}}==
[[Category:{{ja}}|けんり]]
==={{noun}}===
[[Category:{{ja}} {{noun}}|けんり]]
'''[[権]] [[利]]'''（[[けんり]]）
# [[法]]によって[[実行]]が[[保証]]される[[行為]]。
#*権利の[[濫用]]はこれを許さない（日本国民法第一条）
<!--
===={{pron|ja}}==== 
;（アクセント等の記載）
:{{IPA|??}}
:{{X-SAMPA|??}}
-->
===={{etym}}====
*不詳であるが、[[w:西周|西周]]が'''[[right]]'''の訳語として当てはめたものが出版された後、一般的に用いられるようになったとされる。

===={{rel}}====
* [[人権]]、[[生存権]]
* [[物権]]、[[所有権]]、[[債権]]
* {{ant}}:[[義務]]
*{{prov}}:[[権利株]]、[[権利能力]]

===={{trans}}====
{{top}}
*{{bg}}: [[право]] (pravo) ''n'', [[права]] (prava) ''pl.''
*{{de}}: [[Recht]] ''n''
*{{en}}: a [[right]]; a [[claim]]; a [[title]]; a [[privilege]] 
*{{eo}}: [[rajto]]
*{{es}}: [[derecho]] ''m''
*{{fi}}: [[oikeisto]]
*{{fr}}: [[droit]] ''m''
*{{hu}}: [[jog]]
*{{ia}}: [[derecto]]
*{{id}}: [[hak]]
*{{io}}: [[yuro]]
{{mid}}
*{{ko}}: [[권리]] (gweolli) 
*{{la}}: [[jus]]
*{{nl}}: [[recht]] ''n''
*{{pt}}: [[direito]] ''m''
*{{ra}}: [[derecto]] ''m''
*{{ro}}: [[dreaptă]] ''f''
*{{ru}}: [[право]] (právo) ''n'', [[права]] (pravá) ''pl.''
*{{sv}}: [[rätt]] ''c'', [[rättighet]] ''c''
*{{zh}}: [[權利]], [[权利]] (quánlì) 
{{bottom}}
[[Category:{{ja}}_法律|けんり]]
"""
    expected = """
{{wikipedia}}
=={{ja}}==
[[Category:{{ja}}|けんり]]
==={{noun}}===
{{ja-noun|[[けんり]]}}
# [[法]]によって[[実行]]が[[保証]]される[[行為]]。
#*権利の[[濫用]]はこれを許さない（日本国民法第一条）
<!--
===={{pron|ja}}==== 
;（アクセント等の記載）
:{{IPA|??}}
:{{X-SAMPA|??}}
-->
===={{etym}}====
*不詳であるが、[[w:西周|西周]]が'''[[right]]'''の訳語として当てはめたものが出版された後、一般的に用いられるようになったとされる。

===={{rel}}====
* [[人権]]、[[生存権]]
* [[物権]]、[[所有権]]、[[債権]]
* {{ant}}:[[義務]]
*{{prov}}:[[権利株]]、[[権利能力]]

===={{trans}}====
{{top}}
*{{bg}}: [[право]] (pravo) ''n'', [[права]] (prava) ''pl.''
*{{de}}: [[Recht]] ''n''
*{{en}}: a [[right]]; a [[claim]]; a [[title]]; a [[privilege]] 
*{{eo}}: [[rajto]]
*{{es}}: [[derecho]] ''m''
*{{fi}}: [[oikeisto]]
*{{fr}}: [[droit]] ''m''
*{{hu}}: [[jog]]
*{{ia}}: [[derecto]]
*{{id}}: [[hak]]
*{{io}}: [[yuro]]
{{mid}}
*{{ko}}: [[권리]] (gweolli) 
*{{la}}: [[jus]]
*{{nl}}: [[recht]] ''n''
*{{pt}}: [[direito]] ''m''
*{{ra}}: [[derecto]] ''m''
*{{ro}}: [[dreaptă]] ''f''
*{{ru}}: [[право]] (právo) ''n'', [[права]] (pravá) ''pl.''
*{{sv}}: [[rätt]] ''c'', [[rättighet]] ''c''
*{{zh}}: [[權利]], [[权利]] (quánlì) 
{{bottom}}
[[Category:{{ja}}_法律|けんり]]
"""
    mktest(raw, expected)


def test_repl_ja_bold_extra_empty_line() -> None:
    raw = """
=={{ja}}==
[[Category:{{ja}}]]

==={{noun}}===
[[Category:{{ja}} {{noun}}]]
[[Category:{{ja}}_{{noun}}_サ変動詞]]
'''[[愛]] + [[翫]]'''（あいがん）

# [[かわいがる]]こと。
"""
    expected = """
=={{ja}}==
[[Category:{{ja}}]]

==={{noun}}===
{{ja-noun-suru|あいがん}}

# [[かわいがる]]こと。
"""
    mktest(raw, expected)


def test_repl_ja_bold_with_bold_reading() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
[[Category:{{ja}} {{noun}}_サ変動詞]]
'''[[哀]][[鳴]]'''（'''あいめい'''）
"""
    expected = """
==={{noun}}===
{{ja-noun-suru|あいめい}}
"""
    mktest(raw, expected)


def test_repl_ja_bold_with_inner_category() -> None:
    raw = """
==={{noun}}===
[[カテゴリ:{{ja}}_{{noun}}]]
[[カテゴリ:妖怪]]
'''[[赤]] [[手]] [[児]]'''（あかてこ）
#[[青森県]]八戸市に古くから伝わる[[妖怪]]。
"""
    expected = """
==={{noun}}===
{{ja-noun|あかてこ}}
[[カテゴリ:妖怪]]
#[[青森県]]八戸市に古くから伝わる[[妖怪]]。
"""
    mktest(raw, expected)


def test_repl_ja_bold1() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
[[Category:{{ja}} {{noun}}_サ変動詞]]
[[契]] [[約]]（[[けいやく]]）
[[category:{{ja}}_法律|けいやく]]
# [[約束]]であって、それが[[まもる|守ら]]れない[[ばあい|場合]]、[[第三者]]によりそれが[[実現]]されるような[[強制]]がなされるもの。
"""
    expected = """
==={{noun}}===
{{ja-noun-suru|[[けいやく]]}}
[[category:{{ja}}_法律|けいやく]]
# [[約束]]であって、それが[[まもる|守ら]]れない[[ばあい|場合]]、[[第三者]]によりそれが[[実現]]されるような[[強制]]がなされるもの。
"""
    mktest(raw, expected)


# TODO: This is more a question than a skip
# @pytest.mark.skip(reason="not implemented yet, should we keep the hyphen?")
def test_repl_ja_bold2() -> None:
    raw = """
=={{ja}}==
[[Category:{{ja}}|あいさかり]]
==={{noun}}===
[[Category:{{ja}} {{noun}}|あいさかり]]
'''[[愛]][[盛]]り'''【アイザカ-り】
#（特に子女が）もっとも[[愛らしい|愛らしく]]みえる[[年頃]]。かわゆきさかり。
"""
    expected = """
=={{ja}}==
[[Category:{{ja}}|あいさかり]]
==={{noun}}===
{{ja-noun|アイザカ-り}}
#（特に子女が）もっとも[[愛らしい|愛らしく]]みえる[[年頃]]。かわゆきさかり。
"""
    mktest(raw, expected)


def test_repl_ja_adverb1() -> None:
    raw = """
{{DEFAULTSORT:いくえにも {{PAGENAME}}}}
=={{ja}}==
[[Category:{{ja}}]]
==={{adverb}}===
[[Category:{{ja}}_{{adverb}}]]
'''[[幾]][[重]]にも'''（[[いくえ]]にも）
#[[いくつ|幾つ]]も[[かさなる|重なっ]]ていること。
"""
    expected = """
{{DEFAULTSORT:いくえにも {{PAGENAME}}}}
=={{ja}}==
[[Category:{{ja}}]]
==={{adverb}}===
{{ja-adv|[[いくえ]]にも}}
#[[いくつ|幾つ]]も[[かさなる|重なっ]]ていること。
"""
    mktest(raw, expected)


# WARN: Do not change anything.
#
# @pytest.mark.skip(reason="not implemented yet, how to deal with 異表記?")
def test_repl_ja_adverb_with_noise() -> None:
    # https://ja.wiktionary.org/wiki/%E6%80%8F%E6%80%8F
    raw = """
=={{ja}}==
[[Category:{{ja}}|おうおう]]
==={{adverb}}===
[[Category:{{ja}} {{adverb}}|おうおう]]
'''[[怏]] 怏'''（[[おうおう]]　異表記:[[鞅]]鞅）
# 不満足または楽しまぬ様をいう語。
"""
    expected = """
=={{ja}}==
[[Category:{{ja}}|おうおう]]
==={{adverb}}===
[[Category:{{ja}} {{adverb}}|おうおう]]
'''[[怏]] 怏'''（[[おうおう]]　異表記:[[鞅]]鞅）
# 不満足または楽しまぬ様をいう語。
"""
    mktest(raw, expected)


# WARN: Do not change anything.
#
# @pytest.mark.skip(reason="not implemented yet, how to deal with this?")
def test_repl_ja_adjnoun_with_noise() -> None:
    raw = """
==={{adjectivenoun}}===
[[Category:{{ja}}_{{adjectivenoun}}]]
{{jachar|劃一|的}}（かくいつてき {{同音前|[[画一的]]}}）
#「[[画一的]]」の異綴。
"""
    expected = """
==={{adjectivenoun}}===
[[Category:{{ja}}_{{adjectivenoun}}]]
{{jachar|劃一|的}}（かくいつてき {{同音前|[[画一的]]}}）
#「[[画一的]]」の異綴。
"""
    mktest(raw, expected)


# WARN: Do not change anything.
#
# https://ja.wiktionary.org/w/index.php?title=%E6%82%AA%E8%BE%A3&action=edit
#
# I think it should be split over two sections so this is not feasible
# Like here:
# https://ja.wiktionary.org/w/index.php?title=%E6%82%AA%E5%B9%B3%E7%AD%89&action=edit
def test_repl_ja_noun_adjnoun() -> None:
    raw = """
==={{noun}}・{{adjectivenoun}}===
[[category:{{ja}}_{{noun}}]]
[[category:{{ja}}_{{adjectivenoun}}]]
{{jachar|悪|辣}}（'''あくらつ'''）
#たちが悪いこと。[[あくどい]]こと。
"""
    expected = """
==={{noun}}・{{adjectivenoun}}===
[[category:{{ja}}_{{noun}}]]
[[category:{{ja}}_{{adjectivenoun}}]]
{{jachar|悪|辣}}（'''あくらつ'''）
#たちが悪いこと。[[あくどい]]こと。
        """
    mktest(raw, expected)
