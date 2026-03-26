---
title: 藏在殼裏
date: 2026-03-27T03:12:00+08:00
---

<p>
{{< accordion >}}
  {{< accordionItem title="挑戰" open=true >}}

### 描述

和 Shell 交互，獲取旗幟。

### 旗標格式

`PUCTF26{[a-zA-Z0-9_]+_[a-fA-F0-9]{32}}`

### 作者

liyanqwq

  {{< /accordionItem >}}
{{< /accordion >}}
</p>

## 分析

這道題目是一個帶有偽造終端機（terminal）的網站。它提供了一系列的「指令」，不過當中大部份都只是用作惡作劇。例如 `sudo` 和 `b4ckd00r` 指令會開啟一個新分頁並播放 Rick Astley 的《[Never Gonna Give You Up](https://www.youtube.com/watch?v=dQw4w9WgXcQ)》。

![帶有偽造終端機的網站，顯示了一則 MOTD 以及 help 指令的輸出結果](images/shell.png "偽造的終端機")

仔細檢查後，我發現這個網站是使用 [Next.js](https://nextjs.org/) 構建的，並使用了 [Webpack](https://webpack.js.org/) 作為打包工具（bundler）。此外，我還偶然發現了那些指令的實作程式碼。

![Chrome 開發者工具顯示已經載入的檔案及經過混淆的 index.js 檔案](images/obfuscated-index.png "已經載入的檔案及經過混淆的 `index.js` 檔案")

在將 `index.js` 檔案解除混淆後（在此感謝 LLM 的幫助 :smile:），我發現了一個非常可疑的動態 `import()`。目標模組只有在調用 `b4ckd00r` 指令並附帶非空參數時才會被載入。

![解除混淆後的 index.js，顯示了該動態 import](images/deobfuscated-index.png "解除混淆後的 `index.js`")

當我在 `b4ckd00r` 指令後方加上參數後，不出所料，行為發生了改變，而且載入了新的腳本（以及一個 [WebAssembly](https://webassembly.org/) 模組）！它們分別是 `995.js`、`wasm-worker.js`、`wasm_validator.js` 和 `wasm_validator_bg.wasm`，後面三個都是在 [Web Worker](https://developer.mozilla.org/zh-TW/docs/Web/API/Web_Workers_API/Using_web_workers) 中執行的。

![偽造的終端機，顯示了帶有參數的 b4ckd00r 指令的輸出結果](images/shell-b4ckd00r.png "執行帶有參數的 `b4ckd00r` 指令")

![Chrome 開發者工具顯示已經載入的檔案（部分是新加載的）以及經過混淆的 995.js 檔案](images/obfuscated-995.png "新載入的腳本")

從 worker 的腳本當中，我可以看到驗證工作是透過 WebAssembly 模組在背景非同步執行的。儘管反編譯出來的 WebAssembly 模組 C 語言代碼並沒有太大的用處，但它的 C 語言標頭檔卻為我提供了關於導出物件的寶貴線索。這也許已經足夠讓我逆向出題目的旗標了。我們開始破解吧！

![從 WebAssembly 模組中反編譯出來的 C 語言標頭檔](images/validator-header.png "反編譯出來的 C 語言標頭檔")

## 解決方案

根據 worker 中的驗證器，我建立了一個精簡版本，並同時將 WebAssembly 模組的內部記憶體暴露出來：

```js { title="validator.js" }
import fs from "node:fs";

const { instance } = await WebAssembly.instantiate(fs.readFileSync("wasm_validator_bg.wasm"), {});
const validator = instance.exports;
const malloc = validator.__wbindgen_export;

export const memory = validator.memory;

/**
 * @param {string} flag 
 * @returns {boolean}
 */
export function verifyFlag(flag)
{
    const buffer = new TextEncoder().encode(flag);
    const pointer = malloc(buffer.length, 1);
    new Uint8Array(validator.memory.buffer).set(buffer, pointer);
    return Boolean(validator.verify_flag(pointer, buffer.length));
}
```

有了這些，我就可以編寫一個破解腳本，在調用 `verifyFlag()` 函數後讀取它的記憶體：

```js { title="flag-cracker.js" }
import { argv } from "node:process";
import { memory, verifyFlag } from "./validator.js";

const FLAG_PATTERN = /PUCTF26\{[A-Za-z0-9_]+_[a-fA-F0-9]{32}\}/g;

const input = argv.slice(2).join(" ");
console.log("verifyFlag(%o)", input);
console.log("// %o", verifyFlag(input));

console.log();

const memoryString = new TextDecoder("latin1").decode(new Uint8Array(memory.buffer));
const flags = Array.from(memoryString.matchAll(FLAG_PATTERN)).map((matches) => matches[0]);
console.log("Flags in memory:");
flags.forEach((flag) => console.log("- %o", flag));
```

然後透過執行該腳本，您就可以得到旗標了：

```console { title="Terminal" }
> node flag-cracker
verifyFlag('')
// false

Flags in memory:
- 'PUCTF26{C4t_c4T_7h3_w45M_6c138b4309f10ce058582896f8d2e581}'

> node flag-cracker 'PUCTF26{C4t_c4T_7h3_w45M_6c138b4309f10ce058582896f8d2e581}'
verifyFlag('PUCTF26{C4t_c4T_7h3_w45M_6c138b4309f10ce058582896f8d2e581}')
// true

Flags in memory:
- 'PUCTF26{C4t_c4T_7h3_w45M_6c138b4309f10ce058582896f8d2e581}'
- 'PUCTF26{C4t_c4T_7h3_w45M_6c138b4309f10ce058582896f8d2e581}'
- 'PUCTF26{C4t_c4T_7h3_w45M_6c138b4309f10ce058582896f8d2e581}'
```

### 最終旗標

`PUCTF26{C4t_c4T_7h3_w45M_6c138b4309f10ce058582896f8d2e581}`
