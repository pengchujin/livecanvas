# Linux / Windows 生成 Apple Live Photo

目标是生成带 Apple 元数据的 JPEG + MOV，再交给支持配对资源的接收端导入 iPhone 原生照片库。生成与导入是两步；不要把 MT Photos 同名文件合并、MP4 预览或 Android Motion Photo 当作 Apple 原生配对。

## 环境与生成

Python 3.10+、Pillow 10–11、FFmpeg / ffprobe，均应在当前环境可用。不需要 Swift、macOS、照片库或第三方媒体模板。依赖安装在项目虚拟环境，不装进 skill 目录：

```bash
python -m venv .venv
# Linux: .venv/bin/python；Windows PowerShell: .venv\Scripts\python.exe
.venv/bin/python -m pip install 'Pillow>=10,<12'
.venv/bin/python "$SKILL_DIR/scripts/pair_live_photo.py" \
  "$PROJECT_DIR/out/cover.jpg" "$PROJECT_DIR/out/motion.mp4" \
  "$PROJECT_DIR/out/live" 2.6 30
.venv/bin/python "$SKILL_DIR/scripts/package_live_photo.py" \
  "$PROJECT_DIR/out/live" "$PROJECT_DIR/out/主题名称.pvt"
```

Windows PowerShell 示例（路径变量提前设为实际目录；时间/fps 取 render.json）：

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install 'Pillow>=10,<12'
& .\.venv\Scripts\python.exe "$SKILL_DIR/scripts/pair_live_photo.py" "$PROJECT_DIR/out/cover.jpg" "$PROJECT_DIR/out/motion.mp4" "$PROJECT_DIR/out/live" 2.6 30
& .\.venv\Scripts\python.exe "$SKILL_DIR/scripts/package_live_photo.py" "$PROJECT_DIR/out/live" "$PROJECT_DIR/out/主题名称.pvt"
```

随附工具针对 Remotion 的无声 H.264、零起点时间线和同尺寸 JPEG。输出目录必须不存在。拒绝音轨、旋转标记、非 H.264、fps 不匹配、非帧对齐和越界封面时间。视频只重封装，JPEG 高质量重存并保留 ICC；不伪称 JPEG 字节无损。封面必须来自同一 composition 的对应帧，视觉一致性仍要核对。

工具写入：

- JPEG ExifIFD 的 Apple MakerNote tag 17，共享 UUID；MakerNote 使用 TIFF UNDEFINED 类型，避免 Pillow 默认 BYTE 导致 ImageIO 不识别。
- MOV 的 `com.apple.quicktime.content.identifier`。
- `mebx` timed metadata track，`com.apple.quicktime.still-image-time` 为 signed int8 的 0；通过 edit list 定位到 coverTime，样本时长为一帧。

生成后读回标识、轨道、时间；独立用 ffprobe 检查样本时间/时长，用 ffmpeg 完整解码视频；manifest 保存资源哈希。跨平台包脚本重新验证资源，不只相信 `metadataVerified` 标志。不要在写入后再次普通转码 MOV。

## 验证状态

纯 Python 路径设置 `localPHLivePhotoLoad: not_available`，表示没有运行 PhotoKit，不表示 Live Photo 未生成。`.pvt` 是 Python 可以创建的目录包；不能写“.pvt 封装必须 macOS”。已知 PhotoKit 加载失败仍阻止交付，不能用 not_available 掩盖失败。

有 Mac 时可对同一份资源额外验证，无需导入相册：

```bash
swiftc -swift-version 5 "$SKILL_DIR/scripts/verify_live_photo.swift" -o "$PROJECT_DIR/verify-live-photo"
"$PROJECT_DIR/verify-live-photo" "$PROJECT_DIR/out/live"
```

此命令读回 ImageIO/AVFoundation 元数据和 timed sample，再调用 `PHLivePhoto.request`；更新 manifest 的本机验证状态。不改 JPG/MOV，不打开照片 App。

本次实现已在 macOS 上运行纯 Python 生成路径，并由 Apple PhotoKit 独立加载通过；这不是 Linux/Windows 实机运行或 iPhone 导入播放的证明。运行 `scripts/test_portable_live_photo.py` 可检查边界时间、拒绝输入、损坏检测和无 PhotoKit 打包。每次交付仍记录实际环境、接收方式和设备结果。

## iPhone 接收路径

交付同名 `live.jpg` + `live.mov`、manifest 和 `.pvt`，需要传输时创建 ZIP 并保留原始文件。ZIP / `.pvt` 都不是 iPhone「文件」App 一键保存实况的保证；不要让用户把两个文件分别“存储图像/视频”。

接收工具必须将照片作为 `.photo`、视频作为 `.pairedVideo` 加入**同一个** `PHAssetCreationRequest`，或提供等价的 Live Photo 导入能力。该步骤在接收端执行，不要求生成端有 Mac。用户要求直接导入时，确认其实际接收工具并验证，不虚构快捷指令、App 或已安装的导入器。只要求制作文件时无需先获取照片库权限。

MT Photos 可按官方说明将同目录同名 JPG + MOV 合并，iOS App 的下载功能声明可转换为系统支持格式；若用户选择此路径，分别验证服务器识别、iOS 下载保存、照片 App 中 LIVE 和长按播放。服务器动态预览成功不能代替 iPhone 验收。

来源：[Apple 创建配对资源](https://developer.apple.com/documentation/photokit/phassetcreationrequest)、[MT Photos 格式与下载说明](https://mtmt.tech/docs/start/faq/)。底层 Python 模块基于 [video-to-live-photo](https://github.com/yangzhen-23/video-to-live-photo) 的 Apache-2.0 实现，固定源版本 `83b55e6e66b6cbb39e7d7acddbbb52eef1585adc`；已随附许可证与署名，并修正 EXIF 类型、时间样本及读回验证。
