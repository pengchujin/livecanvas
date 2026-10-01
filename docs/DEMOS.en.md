# Demo data & definitions

[简体中文](DEMOS.md) | **English**

Sources for the original nine demos were checked on 2026-09-30. Separate Chinese and English editions preserve the same data and animation timing. Media lives in `demos/zh/` and `demos/en/`. GIFs are 540×720, 15 fps looping previews; MP4s are full resolution. They are not native Live Photo playback in GitHub.

- **Xiaomi:** Total market capitalization in HKD, 2023-09-29 to 2026-09-29. Thirteen quarter-end/latest snapshots; connecting lines are not daily observations. The peak refers only to the sampled points.
- **A20 Pro vs A19 Pro:** Apple’s claims, not independent benchmarks. Each A19 Pro metric is independently normalized to 100. CPU/GPU percentages mean “up to”; the metrics cannot be added together.
- **Population:** UN WPP 2024 historical estimates for 2000/2010/2020; 2025 is a medium-scenario projection. Animated interpolation is not an additional observation.
- **Coffee stores:** 2020–2025 near-year-end counts. Luckin includes Hong Kong from 2024; Starbucks covers mainland China. Reporting dates differ, so no direct ratio is presented. Shop icons mark years.
- **NEV adoption:** Full-year China new-energy passenger-car retail shares, 2021–2025. Includes battery EVs and plug-in hybrids. Each car represents one percentage point; fractional shares partially fill a car.
- **High-speed rail:** Year-end operating length in 2010/2015/2020/2025. The route is a timeline illustration, not a geographic railway map.
- **Temperatures:** 2025 ERA5 daily 2 m temperatures at representative Beijing/Shanghai grid points, averaged by month. Reanalysis, not citywide weather-station measurements.
- **Olympic gold:** CHN Summer Olympic gold medals, 1984–2024, using adjusted counts: Beijing 48, London 39. The Tokyo 2020 edition took place in 2021.
- **Electricity mix:** Actual generation in 2015/2020/2025, not installed capacity. Thermal includes fossil fuels and bioenergy; displayed shares are rounded independently.

For the original nine demos, the Chinese pairs passed macOS PHLivePhoto loading; their English GIF/MP4 previews are not newly paired `.pvt` files, and no iPhone native-playback claim is made. Attribution: [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).


## Sources

- **Xiaomi market cap:** [Stock Analysis](https://stockanalysis.com/quote/hkg/1810/market-cap/)
- **A20 Pro vs A19 Pro:** [Apple Duo](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/), [Apple Pro](https://www.apple.com/newsroom/2026/09/apple-debuts-iphone-18-pro-and-iphone-18-pro-max/)
- **Population:** [UN](https://population.un.org/wpp/), [OWID](https://ourworldindata.org/grapher/population-with-un-projections)
- **Coffee stores:** [Luckin 2025 annual report](https://investor.luckincoffee.co/static-files/7638d701-2f1b-4fd9-99b0-e71a7e77c8ad), [Starbucks FY2026 Q1](https://investor.starbucks.com/news/financial-releases/news-details/2026/Starbucks-Reports-Q1-Fiscal-Year-2026-Results/)
- **NEV adoption:** [CPCA](https://www.cada.cn/Trends/info_91_10424.html), [Annual statistics report](https://www.12365auto.com/news/20260112/561586.shtml)
- **High-speed rail:** [2010](https://www.chinanews.com/gn/2011/01-04/2764471.shtml), [2015/2020](https://www.xinhuanet.com/politics/2021-01/04/c_1126943510.htm), [2025](https://news.cctv.cn/2026/01/04/ARTImeIvsZ3KX3JEIA3zdCC9260104.shtml)
- **Two-city temperatures:** [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)
- **Olympic gold:** [Medal summary](https://en.wikipedia.org/wiki/China_at_the_Olympics#Medals_by_Summer_Games), [Chinese Olympic Committee](https://2024.olympic.cn/china/2024/0812/617045.html)
- **Electricity mix:** [Ember](https://ember-energy.org/data/yearly-electricity-data/), [OWID](https://github.com/owid/energy-data)


## Gemini 4 Argon: six additional demos

Sources checked on 2026-10-01. A1, A2, B1, C1, D1 and E2 appear immediately after the A20 Pro demo. Separate Chinese and English editions use the same data and timing.

| ID | Scope and definitions | Source |
| --- | --- | --- |
| A1 | Gemini 4 Argon announcement: engineering, knowledge work and security. Phased access for trusted testers, not general availability. | [Google announcement](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/) |
| A2 | Output-token limit increases from 64K to 1M. This is not the context-window size. | [Google announcement](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/) |
| B1 | Artificial Analysis Intelligence Index: Argon High 53, GPT-6 Astra Max 53, GPT-6.1 Sol Max 52. The comparison concerns this index, not every task. | [Artificial Analysis post](https://x.com/ArtificialAnlys/status/2105392625788637299) |
| C1 | Omniscience hallucination rate: Argon 15%, Astra 51%, Sol 54%. Denominator: incorrect + partial + not attempted, not all questions. | [Artificial Analysis post](https://x.com/ArtificialAnlys/status/2105392625788637299), [definitions](https://artificialanalysis.ai/evaluations/omniscience) |
| D1 | Text Arena Overall snapshot dated 2026-09-30: Argon High, 1525±9, 4,942 votes, preliminary. Rank does not imply a statistically significant lead. | [Arena Text](https://arena.ai/leaderboard/text) |
| E2 | Terminal-Bench 4.0: Argon High 57%, versus 4% for Gemini 3.1 Pro Preview; a 53-percentage-point increase. | [Artificial Analysis post](https://x.com/ArtificialAnlys/status/2105392625788637299) |

Both language editions of these six cards are 1080×1440, 30 fps and 4 seconds. Covers use frame 102 (3.4 seconds). GIF previews are 540×720 at 15 fps. Each card also includes a `.pvt.zip` download; extract it to obtain the Live Photo resource package. Both languages passed paired-metadata checks, local macOS PHLivePhoto loading and file-hash checks. iPhone playback has not been tested. The looping GIFs on GitHub are previews, not native Live Photo playback.
