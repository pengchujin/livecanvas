# 直接交付实况照片

用户要的是一张可使用的实况照片。JPG + MOV 是内部中间资源；MP4 是预览；ZIP 是传输容器。都不能单独作为“已交付直接 Live 图”的证据。

## 单个 .pvt 实况照片包

`.pvt` 是 Apple Live Photo 包，在文件系统上是一个目录包，不是把 MP4 改后缀，也不是普通 JPEG。包内必须包含已配对的照片、视频与 `metadata.plist`；照片和视频的配对标识、视频内 still-image-time 轨道不能丢失。

```bash
python3 "$SKILL_DIR/scripts/package_live_photo.py" \
  "$PROJECT_DIR/out/live" \
  "$PROJECT_DIR/out/主题名称.pvt" \
  > "$PROJECT_DIR/out/package-receipt.json"
```

原生 Swift 路径接受已通过 metadataVerified 与 PHLivePhoto 本机加载的资源；跨平台 Python 路径重新读回校验元数据、哈希和视频，允许本机加载为 not_available（见 [跨平台生成与 iPhone 接收](portable-live-photo.md)）。已知加载失败不能绕过。脚本复制后校验 SHA-256，不转码；相同输出可安全复用，不覆盖不同内容。`metadata.plist` 使用字符串类型的 `PFVideoComplementMetadataVersionKey = 1`。

包结构参考开源 [makelive 的 .pvt 实现](https://github.com/RhetTbull/makelive/blob/main/makelive/makelive.py)；Apple 定义 [UTType.livePhoto](https://developer.apple.com/documentation/uniformtypeidentifiers/uttype-swift.struct/livephoto)。macOS 文件包可作为单个项目打开/传输；不要承诺所有聊天软件、网页下载器或 iPhone“文件”App 都能直接导入它。ZIP 传输时须明确解压后才得到 .pvt 包。

## 文件验证与完成条件

检查配对 metadata、包内资源哈希与 metadata.plist；有 Apple 环境时补充 `PHLivePhoto.request` 加载，没有时独立记录 not_available。上述加载是对本地文件的验证，不需要往用户照片库写入资产。完成这些检查即可交付实况资源包，但不能据此声称手机可直接预览或已保存为相册中的实况照片。

不要为了验收自动打开 .pvt（可能触发「照片」导入），不启动照片 App、不创建相簿、不修复图库、不请求图库权限。相册导入仅在用户另外明确要求时执行；“直接交付 Live Photo”本身不表示要求导入。

保存 `delivery.json`：交付模式 `file`、包路径、共享 identifier、资源哈希、配对和本机加载验证结果。可选设备验收记为 `not_tested`；未请求的相册导入记为 `not_requested`，不是失败或阻塞。已有历史导入证据不抹除，但不作为新交付的默认流程。

## 回复顺序

1. 优先提供能直接观看的预览，再给 `主题名称.pvt` 的绝对路径链接，标明是实况资源包；iPhone「文件」App 可能显示未知文件。
2. 若传输端不支持目录包，附 `.pvt.zip`；注明解压后得到 .pvt 资源包，仍需要支持该资源的接收应用；ZIP 本身不是实况照片。
3. 需要展示封面 / 视频时标成预览。聊天内不能原生显示 Apple 实况时简短说明，不把 MP4 嵌入说成 Live Photo。
4. 简短注明数据截止日和文件验证范围，不将相册权限、iCloud 或未测手机作为文件交付障碍。
5. 工程、数据、来源及原始资源可附在制作包中，成品链接应独立且容易找到。

用户要求手机直接预览时，文件包交付不是完整验收。网页可使用 Apple LivePhotosKit JS 展示配对资源，但网页播放不等于可保存为原生实况照片；部署或发布遵循用户授权。实际未提供网页时不得宣称已支持。
