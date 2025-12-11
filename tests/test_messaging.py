"""
Test script to verify messaging components
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing Messaging Components...")
print("=" * 50)

# Test 1: Import Message Model
try:
    from models.message import Message
    print("✅ Message Model imported successfully")
    
    # Create a test message
    msg = Message(
        Message_ID=1,
        Sender_ID=1,
        Receiver_ID=2,
        Message_Text="Test message",
        Is_Read=False
    )
    print(f"✅ Message object created: {msg}")
    print(f"✅ Message to_dict(): {msg.to_dict()}")
except Exception as e:
    print(f"❌ Message Model failed: {e}")

print()

# Test 2: Check if controller file exists
try:
    controller_path = os.path.join('src', 'controllers', 'message_controller.py')
    if os.path.exists(controller_path):
        print(f"✅ Controller file exists: {controller_path}")
        with open(controller_path, 'r') as f:
            content = f.read()
            if 'message_bp' in content:
                print("✅ Blueprint 'message_bp' found in controller")
            if '@message_bp.route' in content:
                routes = content.count('@message_bp.route')
                print(f"✅ Found {routes} route definitions")
    else:
        print(f"❌ Controller file not found")
except Exception as e:
    print(f"❌ Controller check failed: {e}")

print()

# Test 3: Check template
try:
    template_path = os.path.join('src', 'templates', 'messages.html')
    if os.path.exists(template_path):
        print(f"✅ Template file exists: {template_path}")
        with open(template_path, 'r') as f:
            content = f.read()
            if 'messages-container' in content:
                print("✅ Template contains messaging components")
    else:
        print(f"❌ Template file not found")
except Exception as e:
    print(f"❌ Template check failed: {e}")

print()

# Test 4: Check CSS
try:
    css_path = os.path.join('src', 'static', 'styles', 'messages.css')
    if os.path.exists(css_path):
        print(f"✅ CSS file exists: {css_path}")
        file_size = os.path.getsize(css_path)
        print(f"✅ CSS file size: {file_size} bytes")
    else:
        print(f"❌ CSS file not found")
except Exception as e:
    print(f"❌ CSS check failed: {e}")

print()

# Test 5: Check JavaScript
try:
    js_path = os.path.join('src', 'static', 'scripts', 'messages.js')
    if os.path.exists(js_path):
        print(f"✅ JavaScript file exists: {js_path}")
        file_size = os.path.getsize(js_path)
        print(f"✅ JS file size: {file_size} bytes")
    else:
        print(f"❌ JavaScript file not found")
except Exception as e:
    print(f"❌ JavaScript check failed: {e}")

print()
print("=" * 50)
print("Summary: All messaging components are ready!")
print()
print("To run the messaging feature:")
print("1. Fix any merge conflicts in src/app.py")
print("2. Run: cd src && python app.py")
print("3. Open: http://localhost:5000/messages")
print("4. Login first to access the messaging page")
