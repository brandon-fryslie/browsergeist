import Foundation
import Darwin

/**
 * Unix Domain Socket Server
 * 
 * Simple BSD socket implementation for IPC communication
 */
class UnixSocketServer {
    private let socketPath: String
    private var serverSocket: Int32 = -1
    private var isRunning = false
    
    init(socketPath: String) {
        self.socketPath = socketPath
    }
    
    func start(handler: @escaping (Int32) -> Void) throws {
        // Remove existing socket
        unlink(socketPath)
        
        // Create socket
        serverSocket = socket(AF_UNIX, SOCK_STREAM, 0)
        guard serverSocket != -1 else {
            throw SocketError.creationFailed
        }
        
        // Setup socket address
        var addr = sockaddr_un()
        addr.sun_family = sa_family_t(AF_UNIX)
        
        let pathBytes = socketPath.utf8CString
        guard pathBytes.count <= MemoryLayout.size(ofValue: addr.sun_path) else {
            throw SocketError.pathTooLong
        }
        
        let pathSize = MemoryLayout.size(ofValue: addr.sun_path)
        withUnsafeMutablePointer(to: &addr.sun_path) { ptr in
            ptr.withMemoryRebound(to: CChar.self, capacity: pathSize) { cPtr in
                pathBytes.withUnsafeBufferPointer { buffer in
                    for (index, byte) in buffer.enumerated() {
                        if index < pathSize {
                            cPtr[index] = byte
                        }
                    }
                }
            }
        }
        
        // Bind socket
        let bindResult = withUnsafePointer(to: &addr) { ptr in
            ptr.withMemoryRebound(to: sockaddr.self, capacity: 1) { sockPtr in
                bind(serverSocket, sockPtr, socklen_t(MemoryLayout<sockaddr_un>.size))
            }
        }
        
        guard bindResult == 0 else {
            close(serverSocket)
            throw SocketError.bindFailed
        }
        
        // Listen for connections
        guard listen(serverSocket, 5) == 0 else {
            close(serverSocket)
            throw SocketError.listenFailed
        }
        
        isRunning = true
        print("Unix socket server listening on \(socketPath)")
        
        // Accept connections
        DispatchQueue.global(qos: .userInitiated).async {
            while self.isRunning {
                let clientSocket = accept(self.serverSocket, nil, nil)
                if clientSocket != -1 {
                    DispatchQueue.global(qos: .userInitiated).async {
                        handler(clientSocket)
                        close(clientSocket)
                    }
                }
            }
        }
    }
    
    func stop() {
        isRunning = false
        if serverSocket != -1 {
            close(serverSocket)
            serverSocket = -1
        }
        unlink(socketPath)
    }
    
    deinit {
        stop()
    }
}

enum SocketError: Error {
    case creationFailed
    case bindFailed
    case listenFailed
    case pathTooLong
}

class SocketConnection {
    private let socket: Int32
    
    init(socket: Int32) {
        self.socket = socket
    }
    
    func readMessage() -> Data? {
        // Read length (4 bytes)
        var lengthBytes = [UInt8](repeating: 0, count: 4)
        guard recv(socket, &lengthBytes, 4, 0) == 4 else {
            return nil
        }
        
        let length = UInt32(bigEndian: lengthBytes.withUnsafeBytes { $0.load(as: UInt32.self) })
        
        // Read message
        var messageBytes = [UInt8](repeating: 0, count: Int(length))
        var totalReceived = 0
        
        while totalReceived < Int(length) {
            let received = recv(socket, &messageBytes[totalReceived], Int(length) - totalReceived, 0)
            guard received > 0 else {
                return nil
            }
            totalReceived += received
        }
        
        return Data(messageBytes)
    }
    
    func sendMessage(_ data: Data) -> Bool {
        let length = UInt32(data.count).bigEndian
        
        // Send length
        var lengthBytes = withUnsafeBytes(of: length) { Array($0) }
        guard send(socket, &lengthBytes, 4, 0) == 4 else {
            return false
        }
        
        // Send data
        let bytes = Array(data)
        return send(socket, bytes, data.count, 0) == data.count
    }
}
