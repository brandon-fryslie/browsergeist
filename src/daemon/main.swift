import Foundation

// Entry point
do {
    let daemon = ControlDaemon()
    try daemon.start()
} catch {
    print("Failed to start daemon: \(error)")
    exit(1)
}
