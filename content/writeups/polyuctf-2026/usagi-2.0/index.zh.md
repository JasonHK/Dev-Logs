---
title: Usagi 2.0
date: 2026-03-08T20:15:00+08:00
---

<p>
{{< accordion >}}
  {{< accordionItem title="挑戰" open=true >}}

### 描述

烏薩奇 呀哈！！ 烏拉烏拉〜♪ 耳朵豎高黃色 衝衝衝 布丁雷達全開 咕嚕咕嚕一口吞！ 蛤？ 吉伊卡哇 抖抖眼淚閃閃，烏薩奇 捏捏捏 欺負 蛤〜？ 無畏跳躍 啪！ 石頭精準 怪物倒地 呀哈哈！！ 小八嘆氣 平靜泡泡啪啪，烏薩奇已經不見蹤影 烏拉啊！！ 回收店詛咒物品 抓抓抓 麻煩上門 普嚕呀〜！ 朋友遇險？ 烏薩奇神速出現 支援 丟丟丟 勝利姿勢 呀哈呀哈！！ 睡哪裡？ 沒人知道 神秘兔子不是兔子 秘密基地 烏拉〜… 飯團偷一口 喀嚓喀嚓消失 衝！ 貪吃模式啟動 食物香氣飄飄 追追追！！ 吉伊卡哇 蛤？ 哭哇哇，烏薩奇 摸頭摸頭 混亂安慰 永遠好朋友 フルルルルァーイ！！

烏薩奇 烏拉！ 布丁杯舔舔 幾秒空空 呀啊啊〜！！ 怪物大吼，耳朵平靜 炸彈棒轉轉轉 轟 勝利！！ 又捏捏欺負 蛤？ 沒人會真的生氣 因為烏薩奇 超強可靠 混亂最佳夥伴 呀哈！！ 烏拉烏拉烏拉〜♪

### 檔案

- [{{< icon "image" >}} usagi2.0.gif](files/usagi2.0.gif)

### 旗幟格式

`PUCTF26{[a-zA-Z0-9_]+_[a-fA-F0-9]{32}}`

  {{< /accordionItem >}}
{{< /accordion >}}
</p>

## 分析

這個 GIF 共有 48 個快速切換的畫面，其中不少其實是重複的；真正與題目有關的，只有最後 3 個不重複的畫面（即經過編碼的旗幟：`ZYrN0vy{Y9L2W_iCOX_wLMkWMt_p_4dRN_kzvByLXcKcyPzey5ecXHfLczPXzBPfzX}`）。

{{< carousel images="images/frames/*" >}}

進一步檢查後，可以發現這個 GIF 實際上是一個「[polyglot](https://en.wikipedia.org/wiki/Polyglot_(computing))」檔案。在十六進位偏移 `2FD04C` 的位置可見文字 `usagi.otf`，而由十六進位偏移 `2FD05D` 開始的二進位資料，則是一個 [OpenType](https://en.wikipedia.org/wiki/OpenType) 字型。這是本題一個非常重要的線索。

![usagi2.0.gif 的十六進位內容，顯示其中夾帶了 OpenType 字型](images/hexdump.png "usagi2.0.gif 的十六進位內容，顯示其中夾帶了 OpenType 字型")

把這個字型用字型檢視工具打開後，便可以立即看出字形次序被打亂了。換言之，距離完整解出題目已經不遠。

![NuttyShell Font 的亂序字形與 Noto Sans 的對照](images/fonts.png "NuttyShell Font 與 Noto Sans 的字形對照")

## 解法

把抽取出來的字型安裝後，可以先在文字編輯器中整理出英數字元之間的對應關係。

![一般字型與 NuttyShell Font 的字元對照](images/editor.png "使用 LibreOffice Writer 建立字元對照")

有了這個對照表之後，便可以寫一個還原字元的程式：

```py { title="unscramble.py" }
#!/usr/bin/env python3
import sys

SCRAMBLED = (
    "p8rwo02U1EsihgCZnJ9NYj73qm" # A-Z
    "L5kAXftbWQ64SMdVFlIRaOxGDT" # a-z
    "eBvPuKyzHc"                 # 0-9
)
ORIGINAL = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
)

TABLE = str.maketrans(SCRAMBLED, ORIGINAL)

def decode(text: str) -> str:
    return text.translate(TABLE)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(decode(" ".join(sys.argv[1:])))
    else:
        for line in sys.stdin:
            print(decode(line), end="")
```

然後執行這個程式，便可以取得旗幟：

```console { title="終端機" }
> ./unscramble.py "ZYrN0vy{Y9L2W_iCOX_wLMkWMt_p_4dRN_kzvByLXcKcyPzey5ecXHfLczPXzBPfzX}"
PUCTF26{USaGi_LOve_Dancing_A_lotT_c7216ae95963706b09e8fa973e713f7e}
```

### 最終旗幟

`PUCTF26{USaGi_LOve_Dancing_A_lotT_c7216ae95963706b09e8fa973e713f7e}`
