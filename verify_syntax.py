# verify_syntax.py - Run this locally before pushing
import os
import py_compile

BASE_DIR = r"F:\simple-sideband\src"

files_to_check = [
    "main.py",
    "networking/lxmf_client.py",
    "networking/reticulum_manager.py",
    "utils/image_handler.py",
]

print("🔍 Checking Python syntax...")
all_good = True

for file in files_to_check:
    path = os.path.join(BASE_DIR, file)
    try:
        py_compile.compile(path, doraise=True)
        print(f"✅ {file}")
    except py_compile.PyCompileError as e:
        print(f"❌ {file}: {e}")
        all_good = False
    except FileNotFoundError:
        print(f"❌ {file}: File not found!")
        all_good = False

if all_good:
    print("\n🎉 All files have valid syntax! Ready to push.")
else:
    print("\n⚠️ Fix syntax errors before pushing to GitHub!")