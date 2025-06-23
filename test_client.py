#!/usr/bin/env python3
"""
SSH Server Test Client
Tests various tunneling capabilities
"""

import asyncio
import asyncssh
import sys
import time


async def test_connection(host='localhost', port=2222, username='admin', password='admin'):
    """Test basic SSH connection"""
    print(f"Testing SSH connection to {host}:{port}")
    
    try:
        async with asyncssh.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            known_hosts=None  # Disable host key checking for testing
        ) as conn:
            print("✓ SSH connection successful!")
            
            # Test basic command execution (should echo back)
            result = await conn.run('test command')
            print(f"✓ Command execution test: {result.stdout.strip()}")
            
            return True
            
    except Exception as e:
        print(f"✗ SSH connection failed: {e}")
        return False


async def test_local_port_forwarding(host='localhost', port=2222, username='admin', password='admin'):
    """Test local port forwarding"""
    print("\nTesting local port forwarding...")
    
    try:
        async with asyncssh.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            known_hosts=None
        ) as conn:
            # Create a local port forward to the SSH server itself
            listener = await conn.forward_local_port('', 0, 'localhost', port)
            local_port = listener.get_port()
            print(f"✓ Local port forwarding active on port {local_port}")
            
            # Test that we can connect to the forwarded port
            # We'll just create the forward and close it quickly
            listener.close()
            await listener.wait_closed()
            print("✓ Local port forwarding test completed")
            
            return True
            
    except Exception as e:
        print(f"✗ Local port forwarding failed: {e}")
        return False


async def test_remote_port_forwarding(host='localhost', port=2222, username='admin', password='admin'):
    """Test remote port forwarding"""
    print("\nTesting remote port forwarding...")
    
    try:
        async with asyncssh.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            known_hosts=None
        ) as conn:
            # Create a remote port forward
            listener = await conn.forward_remote_port('', 0, 'localhost', 22)
            remote_port = listener.get_port()
            print(f"✓ Remote port forwarding active on port {remote_port}")
            
            # Close the forward
            listener.close()
            await listener.wait_closed()
            print("✓ Remote port forwarding test completed")
            
            return True
            
    except Exception as e:
        print(f"✗ Remote port forwarding failed: {e}")
        return False


async def run_all_tests():
    """Run all SSH server tests"""
    print("SSH Server Test Suite")
    print("=" * 50)
    
    tests = [
        test_connection,
        test_local_port_forwarding,
        test_remote_port_forwarding
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"✓ Passed: {sum(results)}")
    print(f"✗ Failed: {len(results) - sum(results)}")
    print(f"Total: {len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! SSH server is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the server configuration.")
        return False


async def interactive_test():
    """Interactive test session"""
    print("\nInteractive SSH Test")
    print("This will keep a connection open for manual testing...")
    
    try:
        async with asyncssh.connect(
            host='localhost',
            port=2222,
            username='admin',
            password='admin',
            known_hosts=None
        ) as conn:
            print("✓ Connected! You can now test tunneling from another terminal:")
            print("\nExample commands to test in another terminal:")
            print("ssh -L 1521:localhost:1521 admin@localhost -p 2222")
            print("ssh -R 8080:localhost:80 admin@localhost -p 2222")
            print("ssh -D 1080 admin@localhost -p 2222")
            print("\nPress Ctrl+C to stop...")
            
            # Keep connection alive
            while True:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\nInteractive test stopped.")
    except Exception as e:
        print(f"Interactive test failed: {e}")


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        asyncio.run(interactive_test())
    else:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
