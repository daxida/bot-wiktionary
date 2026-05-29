import pytest

from wiktbot.reading import repl_reading


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_reading(raw)
    assert expected == received, received


def test_noun() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
{{jachar|思|慮}}（[[しりょ]]）
"""
    expected = """
==={{noun}}===
{{ja-noun|[[しりょ]]}}
"""
    mktest(raw, expected)


def test_noun_raw_header() -> None:
    raw = """
===名詞===
[[Category:{{ja}}_{{noun}}]]
{{jachar|思|慮}}（[[しりょ]]）
"""
    expected = """
==={{noun}}===
{{ja-noun|[[しりょ]]}}
"""
    mktest(raw, expected)


def test_noun_suru1() -> None:
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


def test_noun_suru2() -> None:
    raw = """
=== {{noun}} ===
[[カテゴリ:{{ja}}_{{noun}}|まんそく]]
[[カテゴリ:{{ja}}_{{noun}}_サ変動詞|まんそく]]
'''[[満]] [[足]]'''（[[まんぞく]]）
"""
    expected = """
=== {{noun}} ===
{{ja-noun-suru|[[まんぞく]]}}
"""
    mktest(raw, expected)


def test_noun_suru3() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}} {{noun}}|しんこう]]
[[Category:{{ja}} {{noun}} サ変動詞|しんこう]]
'''[[信]] [[仰]]'''（[[しんこう]]）
"""
    expected = """
==={{noun}}===
{{ja-noun-suru|[[しんこう]]}}
"""
    mktest(raw, expected)


def test_noun_suru_headword_is_kana1() -> None:
    raw = """
==={{noun}}===
{{ja-noun}}【がん[[見]]】
#X
"""
    expected = """
==={{noun}}===
{{ja-noun|がん[[見]]}}
#X
    """
    mktest(raw, expected)


def test_noun_suru_headword_is_kana2() -> None:
    raw = """
==={{noun}}===
{{ja-noun-suru}}【がん[[見]]】
#X
"""
    expected = """
==={{noun}}===
{{ja-noun-suru|がん[[見]]}}
#X
    """
    mktest(raw, expected)


# Unchanged since I'm not sure how to deal with suffixes.
# This is a direct result of is_kana_only logic.
def test_bold_noun_hyphen_in_reading() -> None:
    raw = """
===名詞===
[[category:日本語 名詞]]
[[category:日本語 言語名]]
[[category:{{hi}}|*]]
'''ヒンディー語'''（-ゴ）
"""
    expected = """
===名詞===
[[category:日本語 名詞]]
[[category:日本語 言語名]]
[[category:{{hi}}|*]]
'''ヒンディー語'''（-ゴ）
"""
    mktest(raw, expected)


def test_bold_extra_spaces_with_ascii_parens() -> None:
    raw = """
==日本語==
[[Category:{{ja}}]]

==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
'''[[快]] [[適]]''' (かいてき)
# とても気持ちが良い状態。
    """
    expected = """
==日本語==

==={{noun}}===
{{ja-noun|かいてき}}
# とても気持ちが良い状態。
    """
    mktest(raw, expected)


def test_empty_reading1() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
# 「[[アーキテクチャ]]」の表記ゆれ。
"""
    expected = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
# 「[[アーキテクチャ]]」の表記ゆれ。
"""
    mktest(raw, expected)


def test_empty_reading2() -> None:
    raw = """
==={{noun}}===
[[カテゴリ:{{ja}}_{{noun}}]]
#（'''[[いさご]]'''）細かい[[いし|石]]。[[すな]]。
"""
    expected = """
==={{noun}}===
[[カテゴリ:{{ja}}_{{noun}}]]
#（'''[[いさご]]'''）細かい[[いし|石]]。[[すな]]。
"""
    mktest(raw, expected)


def test_not_kana_in_reading() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
'''[[合]]（い）[[縁]]'''（あいえん 異表記:[[相]][[縁]], [[愛]][[縁]]）
"""
    expected = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
'''[[合]]（い）[[縁]]'''（あいえん 異表記:[[相]][[縁]], [[愛]][[縁]]）
"""
    mktest(raw, expected)


def test_jachar1() -> None:
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
{{kana-DEFAULTSORT|まつび}}
==={{noun}}===
{{ja-noun|まつび}}
#[[文章]]、[[数字]]、[[列]]など、ひと続きになっているものの{{ふりがな|末|すえ}}。[[おわり|終わり]]。[[最後]]。
"""
    mktest(raw, expected)


def test_jachar2() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
{{jachar|特|許}}（とっきょ）
#[[特定]]の人のために[[あたらしい|新しく]][[権利]]を[[設定]]すること。
#新しく[[考案]]された[[発明]]について、考案者に[[独占]]的、[[排他]]的に[[利用]]することを[[みとめる|認める]]こと。
===={{rel}}====
*[[特許権]]
    """
    expected = """
==={{noun}}===
{{ja-noun|とっきょ}}
#[[特定]]の人のために[[あたらしい|新しく]][[権利]]を[[設定]]すること。
#新しく[[考案]]された[[発明]]について、考案者に[[独占]]的、[[排他]]的に[[利用]]することを[[みとめる|認める]]こと。
===={{rel}}====
*[[特許権]]
"""
    mktest(raw, expected)


def test_jachars() -> None:
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
==={{noun}}===
{{ja-noun|さいしゅう}}
#[[一番]]の[[おわり|終わり]]。
===={{pron|jpn}}====
;さ↗いしゅー
"""
    mktest(raw, expected)


def test_jachars_with_file() -> None:
    raw = """
=== {{noun}} ===
[[Category:{{ja}} {{noun}}]]
[[File:水-seal.svg|right|100px]]
{{jachars}}（[[しょうけい]]）
#ものの[[かたち|形]]を[[かたどる]]こと。
"""
    expected = """
=== {{noun}} ===
[[File:水-seal.svg|right|100px]]
{{ja-noun|[[しょうけい]]}}
#ものの[[かたち|形]]を[[かたどる]]こと。
"""
    mktest(raw, expected)


def test_jachars_with_inner_category() -> None:
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


def test_bold_base() -> None:
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
==={{noun}}===
{{ja-noun|[[れんじょう]]}}
#特定の[[ひと|人]]を[[こいしたう|恋い慕う]][[きもち|気持ち]]。
"""
    mktest(raw, expected)


def test_bold_multiple() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}}_{{noun}}|れんしよう れんじょう]]
'''[[恋]] [[情]]'''（[[れんじょう]]）
==={{noun}}===
[[Category:{{ja}}_{{noun}}|れんしよう れんじょう]]
'''[[恋]] [[情]]'''（[[れんじょう]]）
"""
    expected = """
==={{noun}}===
{{ja-noun|[[れんじょう]]}}
==={{noun}}===
{{ja-noun|[[れんじょう]]}}
"""
    mktest(raw, expected)


def test_bold_multiple_mixed() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}}_{{noun}}|れんしよう れんじょう]]
'''[[恋]] [[情]]'''（[[れんじょう]]）
==={{noun}}===
[[Category:{{ja}}_{{noun}}|れんしよう れんじょう]]
{{jachars}} ([[れんじょう]])
"""
    expected = """
==={{noun}}===
{{ja-noun|[[れんじょう]]}}
==={{noun}}===
{{ja-noun|[[れんじょう]]}}
"""
    mktest(raw, expected)


def test_jachar_multiple_readings() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}}_{{noun}}]]
[[Category:{{ja}}_刀剣|ちくとう]]
[[Category:{{ja}}_剣道]]
[[Category:{{ja}}_短剣道]]
[[カテゴリ:常用漢字表 付表|しない]]
{{jachar|竹|刀}}【ちくとう、[[たけがたな]]、[[しない]]】
# （ちくとう、たけがたな）竹製の[[かたな|刀]]。[[竹光]]。
"""
    expected = """
==={{noun}}===
{{ja-noun|ちくとう|[[たけがたな]]|[[しない]]}}
[[Category:{{ja}}_刀剣|ちくとう]]
[[Category:{{ja}}_剣道]]
[[Category:{{ja}}_短剣道]]
[[カテゴリ:常用漢字表 付表|しない]]
# （ちくとう、たけがたな）竹製の[[かたな|刀]]。[[竹光]]。
"""
    mktest(raw, expected)


def test_bold_two_readings() -> None:
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


def test_bold_long() -> None:
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


def test_bold_extra_empty_line1() -> None:
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

==={{noun}}===
{{ja-noun-suru|あいがん}}

# [[かわいがる]]こと。
"""
    mktest(raw, expected)


def test_bold_extra_empty_line2() -> None:
    raw = """
=={{ja}}==
[[Category:{{ja}}]]
==={{noun}}===
[[Category:{{ja}} {{noun}}]]

'''[[執]] [[筆]]'''（しっぴつ） 
#[[文章]]を[[書く]]こと。
"""
    expected = """
=={{ja}}==
==={{noun}}===
{{ja-noun|しっぴつ}}
#[[文章]]を[[書く]]こと。
"""
    mktest(raw, expected)


def test_bold_with_bold_reading() -> None:
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


def test_bold_with_inner_category() -> None:
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


def test_bold_logic_but_no_bold() -> None:
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
def test_bold_with_hyphen() -> None:
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
==={{noun}}===
{{ja-noun|アイザカ-り}}
#（特に子女が）もっとも[[愛らしい|愛らしく]]みえる[[年頃]]。かわゆきさかり。
"""
    mktest(raw, expected)


def test_adverb1() -> None:
    raw = """
==={{adverb}}===
[[Category:{{ja}}_{{adverb}}]]
'''[[幾]][[重]]にも'''（[[いくえ]]にも）
#[[いくつ|幾つ]]も[[かさなる|重なっ]]ていること。
"""
    expected = """
==={{adverb}}===
{{ja-adv|[[いくえ]]にも}}
#[[いくつ|幾つ]]も[[かさなる|重なっ]]ていること。
"""
    mktest(raw, expected)


def test_name1() -> None:
    raw = """
==={{name}}===
{{wikipedia|アフリカ}}
[[category:{{ja}}_{{name}}]]
{{jachars|アフリカ}} (アフリカ)
#'''[[アフリカ]]'''の日本語による漢字表記。
"""
    expected = """
==={{name}}===
{{wikipedia|アフリカ}}
{{ja-name|アフリカ}}
#'''[[アフリカ]]'''の日本語による漢字表記。
"""
    mktest(raw, expected)


@pytest.mark.skip(reason="there is no template for this header, nor the headword")
def test_human_name() -> None:
    raw = """
===人名===
[[Category:{{ja}}_日本語人名|ひてひこ]]
'''英 彦'''（ひでひこ）
#日本人の男性名のひとつ。
"""
    expected = """
===人名===
[[Category:{{ja}}_日本語人名|ひてひこ]]
'''英 彦'''（ひでひこ）
#日本人の男性名のひとつ。
"""
    mktest(raw, expected)


def test_suffix1() -> None:
    raw = """
==={{suffix}}===
[[Category:{{ja}} {{suffix}}]]
{{jachar|気|味}}（ぎみ）
# ある[[傾向]]を帯びていること。
"""
    expected = """
==={{suffix}}===
{{ja-suffix|ぎみ}}
# ある[[傾向]]を帯びていること。
"""
    mktest(raw, expected)


# Follows the final result of:
# https://ja.wiktionary.org/wiki/%E6%84%9F%E5%8B%95%E8%A9%9E#Japanese
# note: uses ascii parens (like the ja-noun template)
def test_with_extra_rare_reading() -> None:
    raw = """
{{Wikipedia|副詞}}
=={{ja}}==
[[Category:{{ja}}|ふくし]]
==={{noun}}===
[[Category:{{ja}}_{{noun}}|ふくし]]
[[Category:{{ja}}_品詞|ふくし]]
'''[[副]] [[詞]]'''【[[ふくし]]、稀:そえことば】
#[[品詞]]の一つ。日本語文法では、[[動詞]]・[[形容詞]]などの[[用言]]
"""
    expected = """
{{Wikipedia|副詞}}
=={{ja}}==
==={{noun}}===
{{ja-noun|[[ふくし]]}} (稀:そえことば)
[[Category:{{ja}}_品詞|ふくし]]
#[[品詞]]の一つ。日本語文法では、[[動詞]]・[[形容詞]]などの[[用言]]
"""
    mktest(raw, expected)


# note: uses ascii parens (like the ja-noun template)
def test_with_extra_old_reading() -> None:
    raw = """
==={{noun}}===
[[Category:{{ja}} {{noun}}]]
{{jachar|気|味}}（きみ、やや古:きび）
#（漢語・原義）[[かおり|香り]]と[[あじ|味]]、[[香気]]と[[風味]]。
"""
    expected = """
==={{noun}}===
{{ja-noun|きみ}} (やや古:きび)
#（漢語・原義）[[かおり|香り]]と[[あじ|味]]、[[香気]]と[[風味]]。
"""
    mktest(raw, expected)


# WARN: Do not change anything.
# (Since there is no replacement, [[Category:{{ja}}|おうおう]] is unchanged)
#
# @pytest.mark.skip(reason="not implemented yet, how to deal with 異表記?")
def test_adverb_with_noise() -> None:
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


def test_adj() -> None:
    raw = """
==={{adj}}===
[[Category:{{ja}} {{adj}}]]
'''[[愛]]くるしい'''（あいくるしい）
# [[愛嬌]]こぼれるばかりである。
"""
    expected = """
==={{adj}}===
{{ja-adj|あいくるしい}}
# [[愛嬌]]こぼれるばかりである。
"""
    mktest(raw, expected)


def test_adj2() -> None:
    raw = """
==={{adjective}}===
{{ja-adj}}【[[若]]い・[[少]]い】
#X
"""
    expected = """
==={{adjective}}===
{{ja-adj|[[若]]い|[[少]]い}}
#X
"""
    mktest(raw, expected)


def test_verb() -> None:
    raw = """
==={{verb}}===
[[Category:{{ja}}_{{verb}}]]
'''[[論]]じる'''（ろんじる）
#X
"""
    expected = """
==={{verb}}===
{{ja-verb|ろんじる}}
#X
"""
    mktest(raw, expected)


def test_idiom1() -> None:
    raw = """
===成句===
[[category:{{ja}}_{{idiom}}]]
[[Category:故事成語]]
[[Category:四字熟語]]
'''[[四]][[面]][[楚]][[歌]]'''（しめんそか）
#X
"""
    expected = """
==={{idiom}}===
{{ja-idiom|しめんそか}}
[[Category:故事成語]]
[[Category:四字熟語]]
#X
    """
    mktest(raw, expected)


def test_idiom2() -> None:
    raw = """
=== {{idiom}} ===
[[Category:{{ja}}_{{idiom}}]]
[[Category:故事成語]]
[[Category:四字熟語]]
'''[[羊]][[頭]][[狗]][[肉]]'''（ようとうくにく）
#X
"""
    expected = """
=== {{idiom}} ===
{{ja-idiom|ようとうくにく}}
[[Category:故事成語]]
[[Category:四字熟語]]
#X
"""
    mktest(raw, expected)


def test_idiom3() -> None:
    raw = """
=={{ja}}==
[[Category:日本語]]
=== {{idiom}} ===
[[Category:{{ja}} {{idiom}}]]
'''[[合]][[縁]][[奇]][[縁]]'''（あいえんきえん）
# [[ひと|人]]と[[ひと|人]]の[[きがあう|気が合う]]のも、[[あう|合わ]]
"""
    expected = """
=={{ja}}==
=== {{idiom}} ===
{{ja-idiom|あいえんきえん}}
# [[ひと|人]]と[[ひと|人]]の[[きがあう|気が合う]]のも、[[あう|合わ]]
"""
    mktest(raw, expected)


# WARN: Do not change anything.
#
# @pytest.mark.skip(reason="not implemented yet, how to deal with this?")
def test_adjnoun_with_noise() -> None:
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
def test_noun_adjnoun() -> None:
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


def test_is_category_removable() -> None:
    raw = """
==={{noun}}===
[[Category:日本語_名詞]]
[[Category:{{ja}} 生理学|*]]
{{jachar|生|理|学}}（[[せいりがく]]）
#X
"""
    expected = """
==={{noun}}===
{{ja-noun|[[せいりがく]]}}
[[Category:{{ja}} 生理学|*]]
#X
"""
    mktest(raw, expected)


def test_head_template() -> None:
    raw = """
==={{noun}}===
{{head|ja|noun|head={{jachars}}}}（[[あいはん]]）
# 「'''[[合印]]'''」に同じ。
#[[連帯]]して[[押印]]すること。
"""
    expected = """
==={{noun}}===
{{ja-noun|[[あいはん]]}}
# 「'''[[合印]]'''」に同じ。
#[[連帯]]して[[押印]]すること。
"""
    mktest(raw, expected)


def test_adnominal() -> None:
    raw = """
===連体詞===
{{head|ja|連体詞}}（しゅたる）
# [[主要]]な。[[おも|主]]な。
"""
    expected = """
==={{adnominal}}===
{{ja-adnominal|しゅたる}}
# [[主要]]な。[[おも|主]]な。
"""
    mktest(raw, expected)


@pytest.mark.skip(reason="ja-proverb doesn't exist (but should)")
def test_proverb() -> None:
    raw = """
=== ことわざ ===
[[Category:{{ja}}_ことわざ]]
'''[[雑魚]]の[[魚]]交じり'''（ザコのトトマじり）
#X
"""
    expected = """
==={{proverb}}===
{{ja-proverb|ザコのトトマじり}}
#X
"""
    mktest(raw, expected)


def test_reading_is_kanji() -> None:
    raw = """
==={{noun}}===
{{ja-noun}}【[[殺]]し[[屋]]】
#X
"""
    expected = """
==={{noun}}===
{{ja-noun|[[殺]]し[[屋]]}}
#X
"""
    mktest(raw, expected)


def test_reading_is_kanji_multiple() -> None:
    raw = """
==={{verb}}===
{{head|ja|verb}}【[[噎]]ぶ、[[咽]]ぶ】
"""
    expected = """
==={{verb}}===
{{ja-verb|[[噎]]ぶ|[[咽]]ぶ}}
"""
    mktest(raw, expected)


def test_reading_is_kanji_multiple_other_separator() -> None:
    raw = """
==={{verb}}・漬ける===
'''つける'''【[[漬]]ける・[[浸]]ける】
"""
    expected = """
==={{verb}}・漬ける===
{{ja-verb|[[漬]]ける|[[浸]]ける}}
"""
    mktest(raw, expected)
