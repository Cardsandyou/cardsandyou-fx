# 卡點遊 每日匯率自動更新

計算機選 ROVE Miles 時，會把美元換算成臺幣。匯率採臺灣銀行美元「即期」匯率，本行買入與賣出取平均。

## 為什麼要另外放一個 GitHub 儲存庫
臺灣銀行網站不允許其他網頁直接從瀏覽器讀取匯率，所以改由 GitHub 每天自動去抓一次，存成 fx.json，網站再讀這個檔。
Publii 每次同步都會覆蓋網站儲存庫（cardsandyou.github.io）的內容，所以這組檔案要放在「另一個」儲存庫：`cardsandyou-fx`。

## 設定步驟（一次就好）
1. 在 GitHub 新增一個公開儲存庫，名稱 `cardsandyou-fx`，勾選 Add a README file。
2. 把這個資料夾裡的檔案上傳到該儲存庫（含 `.github/workflows/update-fx.yml`）。
3. 到儲存庫的 Actions 頁面，選「更新美元匯率」，按 Run workflow 先跑一次，確認儲存庫裡多了 fx.json。
4. 在 Publii：Theme → 計算機 →「每日匯率檔網址（fx.json）」填入
   `https://raw.githubusercontent.com/Cardsandyou/cardsandyou-fx/main/fx.json`
   儲存後按 Sync your website。

之後每天臺灣時間 09:40、16:10 會自動更新。抓取失敗時網站會沿用主題內建的匯率，不會壞掉。

## 備援來源
如果臺灣銀行網站當下連不上，會改用 ExchangeRate-API 的開放版匯率（每日更新一次的市場中間價），計算機上會標示「備援」。
使用這個來源需在網站註明出處，計算機的匯率說明已經自動帶出來源名稱。

## 假日怎麼辦
臺灣銀行假日不掛牌，但網站會維持最後一次掛牌的匯率；fx.json 也會記下掛牌時間，計算機上會顯示是哪一天的匯率。
