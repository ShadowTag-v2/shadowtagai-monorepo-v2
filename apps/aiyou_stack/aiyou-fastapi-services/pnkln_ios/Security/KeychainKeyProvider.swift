import Foundation
import Security
final class KeychainKeyProvider {
    static func fetchOrCreateKey() throws -> Data {
        let tag = "com.pnkln.sqlcipher.key"
        let q:[String:Any] = [kSecClass as String: kSecClassKey, kSecAttrApplicationTag as String: tag, kSecReturnData as String: true]
        var out: CFTypeRef?
        let status = SecItemCopyMatching(q as CFDictionary, &out)
        if status == errSecSuccess, let d = out as? Data { return d }
        var bytes = [UInt8](repeating:0,count:64)
        _ = SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes)
        let key = Data(bytes)
        let add:[String:Any] = [kSecClass as String:kSecClassKey, kSecAttrApplicationTag as String:tag, kSecValueData as String:key, kSecAttrAccessible as String:kSecAttrAccessibleWhenUnlockedThisDeviceOnly]
        SecItemAdd(add as CFDictionary, nil)
        return key
    }
}
