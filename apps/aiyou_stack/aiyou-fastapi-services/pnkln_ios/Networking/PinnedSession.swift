import Foundation
import CryptoKit
final class PinnedSession: NSObject, URLSessionDelegate {
    private let allowedSPKI: Set<String>
    init(allowedSPKI: [String]) { self.allowedSPKI = Set(allowedSPKI) }
    func urlSession(_ s: URLSession, didReceive c: URLAuthenticationChallenge, completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard c.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let trust = c.protectionSpace.serverTrust,
              let cert = SecTrustGetCertificateAtIndex(trust, 0),
              let key = SecCertificateCopyKey(cert),
              let spki = SecKeyCopyExternalRepresentation(key, nil) as Data? else {
            return completionHandler(.cancelAuthenticationChallenge, nil)
        }
        let hash = Data(SHA256.hash(data: spki)).base64EncodedString()
        if allowedSPKI.contains(hash) { completionHandler(.useCredential, URLCredential(trust: trust)) }
        else { completionHandler(.cancelAuthenticationChallenge, nil) }
    }
}
