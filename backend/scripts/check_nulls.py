import os

def main():
    backend_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
    found = False
    # Check both src and tests directories
    for base_dir in [os.path.join(backend_dir, 'src'), os.path.join(backend_dir, 'tests')]:
        for root, _, files in os.walk(base_dir):
            for f in files:
                if not f.endswith('.py'):
                    continue
                p = os.path.join(root, f)
                with open(p, 'rb') as fh:
                    data = fh.read()
                    if b'\x00' in data:
                        idx = data.find(b'\x00')
                        snippet = data[max(0, idx-8):idx+8]
                        print("NULL_BYTE:", p)
                        print("  at offset:", idx)
                        print("  snippet:", snippet[:64])
                        found = True
    if not found:
        print("NO_NULLS_FOUND")

if __name__ == '__main__':
    main()

    main()
