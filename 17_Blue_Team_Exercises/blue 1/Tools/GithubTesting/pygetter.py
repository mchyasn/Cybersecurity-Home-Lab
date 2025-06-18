import os

def get_full_paths(directory='.'):
    full_paths = []
    for filename in os.listdir(directory):
        full_path = os.path.abspath(os.path.join(directory, filename))
        full_paths.append(f'"{full_path}",')
    return full_paths

if __name__ == "__main__":
    paths = get_full_paths()
    for path in paths:
        print(path)
