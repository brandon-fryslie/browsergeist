#!/usr/bin/env python3
"""
Simple keyboard driver test
"""

import socket
import json
import time

def test_keyboard():
    """Simple test of keyboard functionality"""
    print("⌨️ Testing Virtual Keyboard Driver")
    
    try:
        # Connect to daemon
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/browsergeist.sock")
        
        # Test simple typing
        command = {
            "action": "type",
            "text": "Hello from Virtual Keyboard!",
            "delay_profile": "natural"
        }
        
        print("Sending keyboard command...")
        message = json.dumps(command).encode('utf-8')
        length_bytes = len(message).to_bytes(4, byteorder='little')
        sock.send(length_bytes + message)
        
        # Read response
        length_data = sock.recv(4)
        if len(length_data) == 4:
            length = int.from_bytes(length_data, byteorder='little')
            response_data = sock.recv(length)
            response = json.loads(response_data.decode('utf-8'))
            
            if response.get("success"):
                print("✅ Keyboard command successful!")
                print("🎯 Virtual Keyboard Driver is working")
            else:
                print(f"❌ Error: {response.get('error')}")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_keyboard()
