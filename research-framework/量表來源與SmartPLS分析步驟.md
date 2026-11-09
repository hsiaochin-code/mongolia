# 量表來源與 SmartPLS 分析步驟

研究題目：數位時代食品紀念品在旅遊歷程中的角色：以金門貢糖為例
對應架構圖：圖 3-1（H1～H6、H7a、H7b）

> ⚠️ 下列文獻是建議的改編來源。引用前請到學校圖書館資料庫（Google Scholar、ScienceDirect、華藝等）**親自核對原文的作者、年份、期刊與題項內容**，再依金門貢糖的情境改寫題目。

---

## 一、各構面建議的量表來源

| 構面 | 子構面／面向 | 建議改編來源 | 說明 |
|---|---|---|---|
| 數位接觸管道（前置變數） | 網路資訊、社群媒體、電商平台 | 沒有現成的整合量表，建議**自編**，參考 Xiang & Gretzel (2010), *Tourism Management* 的旅遊資訊搜尋研究 | 題目可問各管道的「接觸頻率」與「資訊依賴程度」。自編題目要做**專家效度**和**前測**。建議當作**形成性構面** |
| 食品紀念品刺激（自變數） | 吸引力、地方特色、文化故事、品牌形象 | Swanson & Horridge (2006), *Tourism Management*（紀念品屬性）；Kim & Littrell (2001), *Annals of Tourism Research*；品牌形象參考 Keller (1993), *Journal of Marketing* | 文化故事可以參考「故事行銷（storytelling）」相關研究自行改編 |
| 真實性感知（中介） | — | Kolar & Zabkar (2010), *Tourism Management*；Ram, Björk & Weidenfeld (2016), *Tourism Management* | 兩篇都有現成題項，可以改寫成「金門貢糖讓我感受到道地的金門文化」這類題目 |
| 地方興趣（中介） | — | 沒有公認的標準量表。可以改編涉入程度量表 Zaichkowsky (1985), *Journal of Consumer Research*，或參考目的地好奇心、興趣相關文獻 | **這個構面最需要和指導教授討論**，要先在第二章把操作型定義寫清楚 |
| 地方依附（中介） | 地方認同、地方依賴（可選） | Williams & Vaske (2003), *Forest Science*；Prayag & Ryan (2012), *Journal of Travel Research* | 測量地方依附最常用的經典量表。要決定只用單一構面，還是拆成兩個子構面 |
| 後續行為意圖（依變數） | 推薦意圖、回購意圖、再訪意圖 | Zeithaml, Berry & Parasuraman (1996), *Journal of Marketing*；再訪意圖參考 Chen & Tsai (2007), *Tourism Management* | 回購意圖要涵蓋「線上回購」和「多次購買」兩種情境 |

**題目數量**：每個構面（含子構面）至少 3 題，建議 3～5 題。題目太多問卷會太長，填答品質會變差。

---

## 二、SmartPLS 4 分析步驟清單

### 步驟 0：資料整理（Excel／SPSS）
- [ ] 刪除無效問卷：漏答太多、全部勾同一個選項、填答時間過短
- [ ] 反向題轉換（如果有）
- [ ] 存成 `.csv` 匯入 SmartPLS，第一列放題號（例如 PA1、PA2…）
- [ ] 樣本基本資料的敘述統計（性別、年齡、到訪次數等）

### 步驟 1：共同方法變異（CMV）
- [ ] Harman 單因子檢定（SPSS 用因素分析，第一個因子的解釋變異量 < 50%）
- [ ] 或用全模型共線性檢定：所有 VIF < 3.3（Kock, 2015）

### 步驟 2：建模
- [ ] 照架構圖畫出構面和箭頭：H1～H6，再加上 S → R 的直接路徑
- [ ] 數位接觸管道設定為**形成性**（Mode B），其他構面設定為**反映性**（Mode A）
- [ ] 二階構面（食品紀念品刺激、數位接觸管道、後續行為意圖）用**兩階段法**：
  1. 第一階段：只放一階子構面，跑 PLS 演算法，存下各子構面的潛在變數分數
  2. 第二階段：用這些分數當作二階構面的指標，再跑一次完整模型

### 步驟 3：測量模型（反映性構面）
| 指標 | 標準 |
|---|---|
| 因素負荷量（Outer loadings） | ≥ 0.708（0.4～0.7 之間刪題後 CR/AVE 有改善才刪） |
| Cronbach's α、組合信度 CR（ρc） | 0.70～0.95 |
| 平均變異萃取量 AVE | ≥ 0.50 |
| 區別效度 HTMT | < 0.85（嚴格）或 < 0.90 |

### 步驟 3b：測量模型（形成性構面：數位接觸管道）
- [ ] 指標共線性 VIF < 3.3（最多 < 5）
- [ ] Bootstrap 檢驗各指標的外部權重（outer weights）是否顯著；不顯著時改看外部負荷量是否 ≥ 0.5

### 步驟 4：結構模型
- [ ] 內部共線性 VIF < 5（最好 < 3）
- [ ] **Bootstrap 5,000 次**，看路徑係數、t 值、p 值，檢驗 **H1～H6**
  - 假設都有方向性（正向影響），可以用**單尾檢定**，第三章要寫明
- [ ] 解釋力 R²（0.25 弱、0.50 中、0.75 強）
- [ ] 效果量 f²（0.02 小、0.15 中、0.35 大）
- [ ] 預測力：PLSpredict 的 Q²predict > 0

### 步驟 5：中介效果（H7a、H7b）
- [ ] 在 Bootstrap 結果中打開 **Specific indirect effects** 表格
  - H7a：S → 真實性感知 → 後續行為意圖
  - H7b：S → 真實性感知 → 地方興趣 → 地方依附 → 後續行為意圖
- [ ] 判斷標準：間接效果的 **95% 信賴區間不包含 0**，中介效果就成立
- [ ] 再看 S → R 的直接效果，判斷中介類型（Zhao, Lynch & Chen, 2010）：

| 間接效果 | 直接效果 | 結論 |
|---|---|---|
| 顯著 | 不顯著 | 完全中介 |
| 顯著 | 顯著（同方向） | 部分中介（互補型） |
| 顯著 | 顯著（反方向） | 部分中介（競爭型） |
| 不顯著 | — | 中介不成立 |

### 步驟 6：整理結果
- [ ] 假設檢定總表：假設、路徑、係數、t 值、p 值、是否支持
- [ ] 中介效果表：路徑、間接效果、95% CI、中介類型
- [ ] 結構模型圖：把係數和 R² 標在架構圖上

---

## 三、方法論參考書目（第三章可引用）

- Hair, J. F., Hult, G. T. M., Ringle, C. M., & Sarstedt, M. (2022). *A Primer on Partial Least Squares Structural Equation Modeling (PLS-SEM)* (3rd ed.). Sage.
- Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion for assessing discriminant validity in variance-based structural equation modeling. *Journal of the Academy of Marketing Science*.
- Kock, N. (2015). Common method bias in PLS-SEM: A full collinearity assessment approach. *International Journal of e-Collaboration*.
- Zhao, X., Lynch, J. G., & Chen, Q. (2010). Reconsidering Baron and Kenny: Myths and truths about mediation analysis. *Journal of Consumer Research*.

> 同樣請在引用前核對卷期與頁碼。
