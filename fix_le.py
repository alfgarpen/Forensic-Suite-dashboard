import os

def check_and_fix(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    
    if b'\r' in content:
        print(f"Found CR in {filename}!")
        new_content = content.replace(b'\r', b'')
        with open(filename, 'wb') as f:
            f.write(new_content)
        print(f"Fixed {filename}")
    else:
        print(f"No CR found in {filename}")

check_and_fix('install.sh')
check_and_fix('run.sh')
