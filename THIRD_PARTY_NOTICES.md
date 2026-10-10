# 许可与署名

- 本仓库原创代码、模板和 skill 文档：Copyright © 2026 pengchujin，MIT。
- `docs/demos/` 中的演示图片及视频：原创设计部分由 pengchujin 以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供。转载请署名 LiveCanvas / pengchujin，并保留相关素材署名和统计口径；数据来源的权利、商标及第三方素材不因本仓库许可而转授。
- 人口、咖啡、汽车、高铁、气温、奥运和能源演示中的 emoji：Twitter and Twemoji contributors，[Twemoji](https://github.com/twitter/twemoji)，[CC BY 4.0](docs/licenses/Twemoji-graphics.txt)。图标经布局、缩放及动画编排；未重新绘制其原始图形。城市剪影、汽车阵列和线路示意为本项目原创 SVG。
- 动效设计参考 Emil Kowalski 的 [animate skill](https://github.com/emilkowalski/skills/blob/main/skills/animate/SKILL.md)，按 Remotion 场景制作重新组织；[上游 MIT 许可](docs/licenses/Emil-skills-MIT.txt)。本仓库不附带或要求安装该 skill。
- Live Photo 实现参考 [Apple PhotoKit](https://developer.apple.com/documentation/photos)、[LimitPoint/LivePhoto](https://github.com/LimitPoint/LivePhoto) 及 [RhetTbull/makelive](https://github.com/RhetTbull/makelive) 的格式资料。脚本在本仓库实现，未打包上述工具。
- Remotion、React 等运行依赖不包含在此仓库中，安装时须遵循各自许可证，尤其是 [Remotion 许可](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)。

演示内容为数据与设计示例，不表示相关品牌或机构为本项目背书。数据来源及加工方式见 [DEMOS.md](docs/DEMOS.md)。


## Gemini 4 Argon 演示素材

- `docs/demos/{zh,en}/gemini-argon-*` 中的 Gemini 4 Argon 主图来自 [Google 官方发布](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/)；原图版权归 Google。主图仅做裁切、缩放与动画编排，没有将其列入本项目原创设计的 CC BY 许可。
- 图卡中的 Google 与 OpenAI 标识来自 [Artificial Analysis 模型页](https://artificialanalysis.ai/models/gemini-4-argon) 的品牌素材，用于指明比较对象；商标及素材权利归各自权利人，不因本仓库许可而转授。
- 数据及定义来自 Google、Artificial Analysis 和 Arena。对应链接及评测限制见 [中文演示说明](docs/DEMOS.md#gemini-4-argon新增六张) / [English demo notes](docs/DEMOS.en.md#gemini-4-argon-six-additional-demos)。这些机构不为本项目背书。

## Portable Apple Live Photo metadata

`livecanvas/scripts/portable_live_photo/` includes modified `apple.py` and `iso_bmff.py` from yangzhen-23/video-to-live-photo, commit `83b55e6e66b6cbb39e7d7acddbbb52eef1585adc`, Copyright 2026 杨振, Apache-2.0. License and NOTICE are included in that directory. LiveCanvas modifications cover JPEG ExifIFD/UNDEFINED encoding, zero-valued timed samples, frame-length timing, exact identifier readback, input restrictions and next-track IDs.
