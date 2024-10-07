from os import path


class Config:
    cur_dir = path.dirname(path.abspath(__file__))
    key_path = path.join(cur_dir, '..', '..', 'key.txt')

    with open(key_path) as f:
        KEY = f.read()
