# 演示数据与口径

**简体中文** | [English](DEMOS.en.md)

原有九个演示的制作与来源核对日期：2026-09-30。原有演示提供独立中文、英文版本，分别位于 `demos/zh/` 与 `demos/en/`。两版保留相同数据与动画节奏。README 中的 GIF 由对应 MP4 转换为 540×720、15 fps 的循环预览；JPG 是原始封面，MP4 为高清动画。不宣称 GIF 是原生 Live Photo。

| 演示 | 范围与口径 | 来源 |
| --- | --- | --- |
| 小米市值 | 2023-09-29 至 2026-09-29；13 个季度末/最新样本，总市值、港元。折线连接样本，不是逐日数据。 | [Stock Analysis](https://stockanalysis.com/quote/hkg/1810/market-cap/) |
| A20 Pro vs A19 Pro | 厂商宣称，前代各项独立归一化为 100；CPU/GPU 保留“最高”，非独立跑分。 | [Apple Duo](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/)、[Apple Pro](https://www.apple.com/newsroom/2026/09/apple-debuts-iphone-18-pro-and-iphone-18-pro-max/) |
| 全球人口 | 2000/2010/2020 历史估计、2025 中方案预测；WPP 2024。换位插值不是额外年度观测。 | [UN](https://population.un.org/wpp/)、[OWID](https://ourworldindata.org/grapher/population-with-un-projections) |
| 咖啡门店 | 2020–2025；瑞幸年末中国门店，2024 起含香港；星巴克内地门店使用年末附近财季截止日。日期与地域不完全一致，不计算两者比值。 | [瑞幸 2025 年报](https://investor.luckincoffee.co/static-files/7638d701-2f1b-4fd9-99b0-e71a7e77c8ad)、[星巴克 FY2026 Q1](https://investor.starbucks.com/news/financial-releases/news-details/2026/Starbucks-Reports-Q1-Fiscal-Year-2026-Results/) |
| 新能源车 | 2021–2025 全年新能源乘用车零售渗透率；每辆图标 1 个百分点，末辆部分着色。 | [乘联分会](https://www.cada.cn/Trends/info_91_10424.html)、[全年统计转述](https://www.12365auto.com/news/20260112/561586.shtml) |
| 中国高铁 | 2010/2015/2020/2025 年末营业里程；路径为时间示意，不是真实路线。 | [2010](https://www.chinanews.com/gn/2011/01-04/2764471.shtml)、[2015/2020](https://www.xinhuanet.com/politics/2021-01/04/c_1126943510.htm)、[2025](https://news.cctv.cn/2026/01/04/ARTImeIvsZ3KX3JEIA3zdCC9260104.shtml) |
| 双城气温 | 2025 年 ERA5 北京/上海代表网格日均温按月平均；再分析数据，非全市气象站实测均值。 | [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) |
| 奥运金牌 | CHN 代表团，1984–2024 夏奥会调整后金牌数；北京 48、伦敦 39；东京 2020 届实际在 2021 举行。 | [记录汇总](https://en.wikipedia.org/wiki/China_at_the_Olympics#Medals_by_Summer_Games)、[中国奥委会](https://2024.olympic.cn/china/2024/0812/617045.html) |
| 发电结构 | 2015/2020/2025 年实际发电量；火电含化石燃料和生物质。图中各项独立四舍五入，可能有尾差。 | [Ember](https://ember-energy.org/data/yearly-electricity-data/)、[OWID](https://github.com/owid/energy-data) |

原有九个演示的封面取自各自视频：小米和 A20 Pro 为 2.6 秒，其余七张为 4.6 秒。这九张英文版是 GIF/MP4 预览，未重新配对为 `.pvt`。此前中文配对资源均通过 macOS 本机 PHLivePhoto 加载；未取得这批作品的 iPhone 原生播放验收。素材署名见 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。


## Gemini 4 Argon：新增六张

来源核对日期：2026-10-01。按 A1、A2、B1、C1、D1、E2 顺序，插在 README 的 A20 Pro 演示之后。提供独立中英文图卡，两版数据和动画节奏一致。

| 编号 | 内容与口径 | 来源 |
| --- | --- | --- |
| A1 | Gemini 4 Argon 发布；软件工程、知识工作与安全防御。分阶段开放给受信任测试者，不表示全面公开可用。 | [Google 发布](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/) |
| A2 | 输出 token 上限从 64K 提高到 1M；不是上下文窗口大小。 | [Google 发布](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/) |
| B1 | Artificial Analysis 智能指数：Argon High 53、GPT-6 Astra Max 53、GPT-6.1 Sol Max 52。比较限定于该指数，不表示所有任务表现相同。 | [Artificial Analysis 原帖](https://x.com/ArtificialAnlys/status/2105392625788637299) |
| C1 | Omniscience 幻觉率：Argon 15%、Astra 51%、Sol 54%。分母为错误、部分回答和未作答之和，不是所有题目。 | [Artificial Analysis 原帖](https://x.com/ArtificialAnlys/status/2105392625788637299)、[指标定义](https://artificialanalysis.ai/evaluations/omniscience) |
| D1 | Text Arena Overall，2026-09-30 快照：Argon High 1525±9，4,942 票，初步结果。排名不表示统计显著领先。 | [Arena Text](https://arena.ai/leaderboard/text) |
| E2 | Terminal-Bench 4.0：Argon High 57%，此前 Gemini 3.1 Pro Preview 4%，提高 53 个百分点。 | [Artificial Analysis 原帖](https://x.com/ArtificialAnlys/status/2105392625788637299) |

这六张的中英文版本均为 1080×1440、30 fps、4 秒；封面取第 102 帧（3.4 秒）。GIF 为 540×720、15 fps 预览。每张另附 `.pvt.zip`，解压得到 Live Photo 资源包。两种语言的包均通过元数据配对、macOS PHLivePhoto 本机加载与哈希验证；未测试 iPhone 原生播放。GitHub 中循环播放的 GIF 不是原生 Live Photo。
