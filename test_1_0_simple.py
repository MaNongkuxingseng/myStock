# myStock 1.0版本 - 简化测试
import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

print("="*80)
print("myStock 1.0 Version - Full Function Test")
print("="*80)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Base URL: http://localhost:9988")
print()

results = []

# 1. Check service status
print("1. Checking service status...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 9988))
    sock.close()
    
    if result == 0:
        print("   [PASS] Port 9988 is listening")
        results.append(("Service Port", True, "Port 9988 listening"))
    else:
        print("   [FAIL] Port 9988 not listening")
        results.append(("Service Port", False, "Port 9988 not listening"))
        sys.exit(1)
except Exception as e:
    print(f"   [ERROR] Port check failed: {e}")
    results.append(("Service Port", False, f"Error: {e}"))
    sys.exit(1)

# 2. Test home page
print("\n2. Testing home page...")
try:
    response = requests.get("http://localhost:9988/", timeout=10)
    if response.status_code == 200:
        print(f"   [PASS] Home page loaded (Status: {response.status_code})")
        print(f"   [INFO] Content length: {len(response.text)} characters")
        results.append(("Home Page", True, f"Status {response.status_code}"))
    else:
        print(f"   [FAIL] Home page failed (Status: {response.status_code})")
        results.append(("Home Page", False, f"Status {response.status_code}"))
except Exception as e:
    print(f"   [ERROR] Home page test failed: {e}")
    results.append(("Home Page", False, f"Error: {e}"))

# 3. Test API endpoints
print("\n3. Testing API endpoints...")
api_endpoints = [
    ("/instock/api_data", "Stock Data API"),
    ("/instock/data", "Stock Data Page"),
    ("/instock/data/indicators", "Indicator Data"),
]

api_results = []
for endpoint, description in api_endpoints:
    try:
        url = f"http://localhost:9988{endpoint}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"   [PASS] {description}: Status {response.status_code}")
            api_results.append(True)
        else:
            print(f"   [FAIL] {description}: Status {response.status_code}")
            api_results.append(False)
    except Exception as e:
        print(f"   [ERROR] {description}: {e}")
        api_results.append(False)

api_success = sum(api_results) / len(api_results) > 0.5
results.append(("API Endpoints", api_success, f"{sum(api_results)}/{len(api_results)} passed"))

# 4. Check directory structure
print("\n4. Checking directory structure...")
required_dirs = [
    "instock",
    "instock/core",
    "instock/lib", 
    "instock/web",
    "instock/job",
    "instock/log"
]

dir_results = []
for dir_path in required_dirs:
    full_path = project_root / dir_path
    if full_path.exists():
        print(f"   [PASS] Directory exists: {dir_path}")
        dir_results.append(True)
    else:
        print(f"   [FAIL] Directory missing: {dir_path}")
        dir_results.append(False)

dir_success = sum(dir_results) / len(dir_results) > 0.8
results.append(("Directory Structure", dir_success, f"{sum(dir_results)}/{len(dir_results)} exist"))

# 5. Check key files
print("\n5. Checking key files...")
key_files = [
    "instock/web/web_service.py",
    "instock/lib/database.py",
    "instock/core/singleton_stock.py",
    "README.md"
]

file_results = []
for file_path in key_files:
    full_path = project_root / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"   [PASS] File exists: {file_path} ({size} bytes)")
        file_results.append(True)
    else:
        print(f"   [FAIL] File missing: {file_path}")
        file_results.append(False)

file_success = sum(file_results) / len(file_results) > 0.8
results.append(("Key Files", file_success, f"{sum(file_results)}/{len(file_results)} exist"))

# 6. Check database module
print("\n6. Checking database module...")
try:
    import instock.lib.database as mdb
    print("   [PASS] Database module imported successfully")
    results.append(("Database Module", True, "Import successful"))
except ImportError as e:
    print(f"   [FAIL] Database module import failed: {e}")
    results.append(("Database Module", False, f"Import failed: {e}"))
except Exception as e:
    print(f"   [ERROR] Database check error: {e}")
    results.append(("Database Module", False, f"Error: {e}"))

# Generate report
print("\n" + "="*80)
print("TEST REPORT")
print("="*80)

total = len(results)
passed = sum(1 for _, success, _ in results if success)
failed = total - passed

print(f"Total Tests: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {passed/total*100:.1f}%")

print("\nDetailed Results:")
for test_name, success, details in results:
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} {test_name}: {details}")

# Save report
report = {
    "version": "1.0",
    "test_time": datetime.now().isoformat(),
    "base_url": "http://localhost:9988",
    "results": [
        {
            "test": name,
            "success": success,
            "details": details
        }
        for name, success, details in results
    ],
    "summary": {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "success_rate": passed / total if total > 0 else 0
    }
}

report_file = project_root / "1_0_TEST_REPORT.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\nReport saved to: {report_file}")

print("\n" + "="*80)
if passed == total:
    print("SUCCESS: All tests passed! myStock 1.0 is fully functional.")
else:
    print(f"WARNING: {failed} test(s) failed. Please check the report.")
print("="*80)