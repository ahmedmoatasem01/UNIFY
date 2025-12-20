"""
Diagnostic script to test connection to Hugging Face and identify issues.
"""
import sys
import socket
import urllib.request
import urllib.error

def test_internet_connection():
    """Test basic internet connectivity"""
    print("=" * 60)
    print("Testing Internet Connection")
    print("=" * 60)
    
    # Test 1: DNS Resolution
    print("\n1. Testing DNS resolution for huggingface.co...")
    try:
        ip = socket.gethostbyname('huggingface.co')
        print(f"   ✓ DNS resolved: huggingface.co -> {ip}")
    except socket.gaierror as e:
        print(f"   ✗ DNS resolution failed: {e}")
        print("   → This suggests a DNS or network connectivity issue")
        return False
    
    # Test 2: HTTP Connection
    print("\n2. Testing HTTP connection to huggingface.co...")
    try:
        req = urllib.request.Request('https://huggingface.co', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            print(f"   ✓ HTTP connection successful (Status: {status})")
    except urllib.error.URLError as e:
        print(f"   ✗ HTTP connection failed: {e}")
        if "timeout" in str(e).lower():
            print("   → Connection timed out - check firewall/proxy settings")
        elif "SSL" in str(e) or "certificate" in str(e).lower():
            print("   → SSL/Certificate issue - may need to update certificates")
        else:
            print("   → Network connectivity issue")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False
    
    # Test 3: Hugging Face API
    print("\n3. Testing Hugging Face API endpoint...")
    try:
        api_url = 'https://huggingface.co/api/models/sshleifer/distilbart-cnn-12-6'
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            print(f"   ✓ API endpoint accessible (Status: {status})")
    except Exception as e:
        print(f"   ✗ API endpoint failed: {e}")
        print("   → Hugging Face API may be blocked or unreachable")
        return False
    
    return True

def test_transformers_import():
    """Test if transformers library can be imported"""
    print("\n4. Testing transformers library...")
    try:
        from transformers import pipeline, AutoTokenizer
        print("   ✓ transformers library imported successfully")
        return True
    except ImportError as e:
        print(f"   ✗ Failed to import transformers: {e}")
        print("   → Run: pip install transformers")
        return False

def check_proxy_settings():
    """Check for proxy settings"""
    print("\n5. Checking proxy settings...")
    import os
    
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy or https_proxy:
        print(f"   ⚠ Proxy detected:")
        if http_proxy:
            print(f"      HTTP_PROXY: {http_proxy}")
        if https_proxy:
            print(f"      HTTPS_PROXY: {https_proxy}")
        print("   → If you're behind a proxy, transformers may need proxy configuration")
    else:
        print("   ✓ No proxy settings detected")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("Hugging Face Connection Diagnostic Tool")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Internet Connection", test_internet_connection()))
    results.append(("Transformers Library", test_transformers_import()))
    check_proxy_settings()
    
    # Summary
    print("\n" + "=" * 60)
    print("Diagnostic Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! You should be able to download the model.")
        print("\nTry running: python download_model.py")
    else:
        print("Some tests failed. See recommendations below:")
        print("\nRECOMMENDATIONS:")
        print("1. Check your internet connection")
        print("2. If on a corporate network, contact IT about firewall/proxy")
        print("3. Try using a VPN if huggingface.co is blocked in your region")
        print("4. Check Windows Firewall settings")
        print("5. Try running as administrator")
        print("\nAlternative: Download model manually from:")
        print("   https://huggingface.co/sshleifer/distilbart-cnn-12-6")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

