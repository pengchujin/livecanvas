# LiveCanvas · 实况画布

**简体中文** | [English](README.en.md)

**一句话，做成有封面、有动画的 Live 图**

一个适用于 Codex、Claude Code 等 AI 编程助手的 skill：**搜索核实 → 设计分镜 → Remotion 动画 → 预览与 Apple Live Photo 资源**。支持图片、emoji、场景、时间线和图表。

## 作品演示

9 张中文作品，GIF 直接循环播放；点击标题查看高清 MP4。切换到 [English](README.en.md) 可查看英文版作品。

| [小米市值](docs/demos/zh/xiaomi.mp4) | [A20 Pro vs A19 Pro](docs/demos/zh/a20-pro.mp4) | [全球人口](docs/demos/zh/population.mp4) |
| :---: | :---: | :---: |
| ![小米市值](docs/demos/zh/xiaomi.gif) | ![A20 Pro vs A19 Pro](docs/demos/zh/a20-pro.gif) | ![全球人口](docs/demos/zh/population.gif) |

| [咖啡门店](docs/demos/zh/coffee.mp4) | [新能源车](docs/demos/zh/nev.mp4) | [中国高铁](docs/demos/zh/rail.mp4) |
| :---: | :---: | :---: |
| ![咖啡门店](docs/demos/zh/coffee.gif) | ![新能源车](docs/demos/zh/nev.gif) | ![中国高铁](docs/demos/zh/rail.gif) |

| [双城气温](docs/demos/zh/weather.mp4) | [奥运金牌](docs/demos/zh/olympics.mp4) | [发电结构](docs/demos/zh/energy.mp4) |
| :---: | :---: | :---: |
| ![双城气温](docs/demos/zh/weather.gif) | ![奥运金牌](docs/demos/zh/olympics.gif) | ![发电结构](docs/demos/zh/energy.gif) |

数据为制作时的快照，不会自动更新。来源与口径见 [演示说明](docs/DEMOS.md)。

## 安装

需要 Node.js / npm。使用 [Skills CLI](https://github.com/vercel-labs/skills) 安装，并选择你的 AI 助手：

```bash
npx skills add pengchujin/livecanvas --skill livecanvas -g
```

只装到 Codex：

```bash
npx skills add pengchujin/livecanvas --skill livecanvas -g -a codex
```

安装后新建对话，输入：

```text
用 LiveCanvas 做北京和上海去年全年气温变化。
加入城市插画和季节 emoji，设计完整封面，并提供动态预览。
```

<details>
<summary>手动安装到 Codex</summary>

下载或克隆本仓库，把整个 `livecanvas/` 文件夹放入 `~/.codex/skills/`；若设置了 `CODEX_HOME`，则放入该目录下的 `skills/`。不要只复制 SKILL.md。随后新建对话。

需要兼容旧的 `$livechart` 调用时，再把 `livechart/` 文件夹放到同一位置。

</details>

## 运行与交付

- **动画：** 助手需能联网搜索和执行代码；需 Node.js、Python 3、FFmpeg，以及内容对应的字体。项目用 `npm ci` 安装依赖。
- **Live Photo：** 配对封装额外需要 macOS 和 Xcode Command Line Tools。当前工具支持无声 H.264 + JPEG。
- **交付：** 封面、MP4、数据来源、可编辑工程，以及支持环境下的 `.pvt` 资源包；不自动导入相册。

`.pvt` 包含配对照片、视频及元数据，iPhone「文件」App 未必能直接预览。README 使用 GIF 展示动效，GIF 不是原生 Live Photo。

模板使用 Remotion 4.0.530。手动渲染与封装步骤见 [运行指南](livecanvas/references/production.md)。

## 许可与致谢

代码及 skill 文档采用 [MIT](LICENSE)；演示媒体与第三方素材许可见 [署名说明](THIRD_PARTY_NOTICES.md)。Remotion 适用其[自身许可证](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)。

动效设计参考 [Emil Kowalski / animate](https://github.com/emilkowalski/skills/blob/main/skills/animate/SKILL.md)，图标采用 [Twemoji](https://github.com/twitter/twemoji)。
