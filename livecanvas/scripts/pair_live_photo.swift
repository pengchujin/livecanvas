// macOS, silent H.264 + JPEG only. Writes new files; never imports into Photos.
import Foundation
import AVFoundation
import ImageIO
import Photos
import AppKit
import UniformTypeIdentifiers

struct Failure: Error, CustomStringConvertible { let description: String }
func check(_ ok: Bool, _ message: String) throws { if !ok { throw Failure(description: message) } }
func writeJSON(_ object: [String: Any], _ url: URL) throws {
    try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys]).write(to: url)
}
func waitReady(_ input: AVAssetWriterInput, writer: AVAssetWriter) throws {
    let deadline = Date().addingTimeInterval(30)
    while !input.isReadyForMoreMediaData {
        try check(writer.status == .writing, "Writer failed: \(String(describing: writer.error))")
        try check(Date() < deadline, "Writer readiness timed out")
        Thread.sleep(forTimeInterval: 0.002)
    }
}

func run() throws {
    let args = CommandLine.arguments
    guard args.count == 6 else {
        print("Usage: pair_live_photo COVER.jpg MOTION.mp4 NEW_OUTPUT_DIRECTORY COVER_SECONDS FPS")
        throw Failure(description: "Expected five arguments")
    }
    let photo = URL(fileURLWithPath: args[1]), movie = URL(fileURLWithPath: args[2])
    let output = URL(fileURLWithPath: args[3], isDirectory: true)
    guard let seconds = Double(args[4]), let fps = Double(args[5]) else { throw Failure(description: "Invalid time/fps") }
    try check(seconds.isFinite && fps.isFinite && fps > 0 && fps <= 240, "Invalid time/fps")
    try check(!FileManager.default.fileExists(atPath: output.path), "Output directory already exists; choose a new directory")
    let asset = AVURLAsset(url: movie)
    let duration = CMTimeGetSeconds(asset.duration)
    try check(duration.isFinite && seconds >= 0 && seconds + 1/fps <= duration + 0.0001, "Cover time outside video")
    try check(asset.tracks(withMediaType: .audio).isEmpty, "Audio present: this helper is silent-only; use an audio-preserving writer")
    guard let track = asset.tracks(withMediaType: .video).first,
          let rawFormat = track.formatDescriptions.first else { throw Failure(description: "Missing video track") }
    let format = rawFormat as! CMFormatDescription
    try check(CMFormatDescriptionGetMediaSubType(format) == kCMVideoCodecType_H264, "Expected H.264 input")
    try check(abs(Double(track.nominalFrameRate)-fps) < 0.1, "FPS does not match input")
    try check(abs(CMTimeGetSeconds(track.timeRange.start)) < 0.0001, "Expected a zero-based Remotion timeline")
    try check(abs(seconds*fps - (seconds*fps).rounded()) < 0.0001, "Cover time must align to a video frame")
    guard let source = CGImageSourceCreateWithURL(photo as CFURL, nil),
          let sourceType = CGImageSourceGetType(source),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { throw Failure(description: "Cannot read cover") }
    try check(sourceType as String == UTType.jpeg.identifier, "Cover must be JPEG")
    let transformed = track.naturalSize.applying(track.preferredTransform)
    try check(image.width == Int(abs(transformed.width).rounded()) && image.height == Int(abs(transformed.height).rounded()), "Cover/video dimensions differ")
    try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
    let imageURL = output.appendingPathComponent("live.jpg"), videoURL = output.appendingPathComponent("live.mov")
    let identifier = UUID().uuidString
    var properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any] ?? [:]
    var maker = properties[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any] ?? [:]
    maker["17"] = identifier
    properties[kCGImagePropertyMakerAppleDictionary as String] = maker
    properties[kCGImageDestinationLossyCompressionQuality as String] = 1.0
    guard let dest = CGImageDestinationCreateWithURL(imageURL as CFURL, UTType.jpeg.identifier as CFString, 1, nil) else { throw Failure(description: "Cannot create JPEG") }
    CGImageDestinationAddImageFromSource(dest, source, 0, properties as CFDictionary)
    try check(CGImageDestinationFinalize(dest), "JPEG write failed")

    let reader = try AVAssetReader(asset: asset)
    let readVideo = AVAssetReaderTrackOutput(track: track, outputSettings: nil)
    readVideo.alwaysCopiesSampleData = false
    try check(reader.canAdd(readVideo), "Cannot add video reader")
    reader.add(readVideo)
    let writer = try AVAssetWriter(outputURL: videoURL, fileType: .mov)
    let content = AVMutableMetadataItem()
    content.keySpace = .quickTimeMetadata
    content.key = AVMetadataKey.quickTimeMetadataKeyContentIdentifier as NSString
    content.value = identifier as NSString
    content.dataType = kCMMetadataBaseDataType_UTF8 as String
    writer.metadata = [content]
    let videoInput = AVAssetWriterInput(mediaType: .video, outputSettings: nil, sourceFormatHint: format)
    videoInput.transform = track.preferredTransform
    videoInput.expectsMediaDataInRealTime = false
    try check(writer.canAdd(videoInput), "Cannot add video writer")
    writer.add(videoInput)
    let spec: [String: Any] = [kCMMetadataFormatDescriptionMetadataSpecificationKey_Identifier as String: "mdta/com.apple.quicktime.still-image-time", kCMMetadataFormatDescriptionMetadataSpecificationKey_DataType as String: kCMMetadataBaseDataType_SInt8 as String]
    var metadataFormat: CMFormatDescription?
    let status = CMMetadataFormatDescriptionCreateWithMetadataSpecifications(allocator: kCFAllocatorDefault, metadataType: kCMMetadataFormatType_Boxed, metadataSpecifications: [spec] as CFArray, formatDescriptionOut: &metadataFormat)
    try check(status == noErr && metadataFormat != nil, "Cannot create timed metadata format")
    let metadataInput = AVAssetWriterInput(mediaType: .metadata, outputSettings: nil, sourceFormatHint: metadataFormat)
    let adaptor = AVAssetWriterInputMetadataAdaptor(assetWriterInput: metadataInput)
    try check(writer.canAdd(metadataInput), "Cannot add metadata writer")
    writer.add(metadataInput)
    try check(writer.startWriting(), "Cannot start writer")
    writer.startSession(atSourceTime: .zero)
    try check(reader.startReading(), "Cannot start reader")
    let still = AVMutableMetadataItem()
    still.keySpace = .quickTimeMetadata
    still.key = "com.apple.quicktime.still-image-time" as NSString
    still.value = NSNumber(value: Int8(0))
    still.dataType = kCMMetadataBaseDataType_SInt8 as String
    let keyTime = CMTime(seconds: seconds, preferredTimescale: 60000)
    try waitReady(metadataInput, writer: writer)
    try check(adaptor.append(AVTimedMetadataGroup(items: [still], timeRange: CMTimeRange(start: keyTime, duration: CMTime(seconds: 1/fps, preferredTimescale: 60000)))), "Cannot append still-image-time")
    metadataInput.markAsFinished()
    while let sample = readVideo.copyNextSampleBuffer() {
        try waitReady(videoInput, writer: writer)
        try check(videoInput.append(sample), "Cannot append video sample")
    }
    try check(reader.status == .completed, "Reader failed: \(String(describing: reader.error))")
    videoInput.markAsFinished()
    let done = DispatchSemaphore(value: 0)
    writer.finishWriting { done.signal() }
    try check(done.wait(timeout: .now()+60) == .success && writer.status == .completed, "Writer completion failed: \(String(describing: writer.error))")

    // Read back both identifiers and actual timed metadata sample position.
    let imageCheck = CGImageSourceCreateWithURL(imageURL as CFURL, nil)!
    let imageProps = CGImageSourceCopyPropertiesAtIndex(imageCheck, 0, nil) as? [String: Any]
    let imageID = (imageProps?[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any])?["17"] as? String
    let paired = AVURLAsset(url: videoURL)
    let videoID = paired.metadata(forFormat: .quickTimeMetadata).first { $0.identifier == .quickTimeMetadataContentIdentifier }?.stringValue
    try check(imageID == identifier && videoID == identifier, "Readback identifier mismatch")
    var actualTime: Double?
    for metadataTrack in paired.tracks(withMediaType: .metadata) {
        let mr = try AVAssetReader(asset: paired)
        let mo = AVAssetReaderTrackOutput(track: metadataTrack, outputSettings: nil)
        mr.add(mo)
        let ma = AVAssetReaderOutputMetadataAdaptor(assetReaderTrackOutput: mo)
        try check(mr.startReading(), "Metadata readback failed")
        while let group = ma.nextTimedMetadataGroup() {
            if group.items.contains(where: { $0.key as? String == "com.apple.quicktime.still-image-time" }) {
                actualTime = CMTimeGetSeconds(group.timeRange.start)
            }
        }
        try check(mr.status == .completed, "Incomplete metadata readback")
    }
    try check(actualTime != nil && abs(actualTime!-seconds) < 1/fps, "Still time missing or incorrect")
    var loaded = false, completed = false, loadError: String?
    let request = PHLivePhoto.request(withResourceFileURLs: [imageURL, videoURL], placeholderImage: nil, targetSize: .zero, contentMode: .aspectFit) { live, info in
        if (info[PHLivePhotoInfoIsDegradedKey] as? Bool) == true { return }
        loaded = live != nil
        loadError = (info[PHLivePhotoInfoErrorKey] as? Error)?.localizedDescription
        completed = true
    }
    let deadline = Date().addingTimeInterval(30)
    while !completed && Date() < deadline { RunLoop.current.run(until: Date().addingTimeInterval(0.05)) }
    if !completed { PHLivePhoto.cancelRequest(withRequestID: request); loadError = "PHLivePhoto loading timed out" }
    let manifest: [String: Any] = ["identifier": identifier, "photo": "live.jpg", "video": "live.mov", "coverTime": seconds, "readbackStillTime": actualTime!, "duration": duration, "fps": fps, "metadataVerified": true, "localPHLivePhotoLoad": loaded ? "passed" : "failed", "loadError": loadError ?? "", "iPhonePlayback": "not_tested", "wallpaper": "not_tested", "importedIntoPhotos": false]
    try writeJSON(manifest, output.appendingPathComponent("manifest.json"))
    print(String(data: try JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted,.sortedKeys]), encoding: .utf8)!)
    try check(loaded, "Resources created and metadata verified, but local PHLivePhoto loading failed; see manifest")
}
do { try run() } catch { fputs("LiveCanvas: \(error)\n", stderr); exit(1) }
