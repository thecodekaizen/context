import Foundation
import Vision
import ImageIO

var output: [[String: Any]] = []
for path in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: path)
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    do {
        try VNImageRequestHandler(url: url, options: [:]).perform([request])
        let rows: [[String: Any]] = (request.results ?? []).compactMap { item in
            guard let candidate = item.topCandidates(1).first else { return nil }
            let b = item.boundingBox
            return ["text": candidate.string, "box": [b.minX, 1-b.maxY, b.maxX, 1-b.minY]]
        }
        output.append(["file": url.lastPathComponent, "rows": rows])
    } catch {
        FileHandle.standardError.write(Data("Local OCR failed\n".utf8))
        exit(1)
    }
}
let data = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
FileHandle.standardOutput.write(data)
