#! /usr/bin/env python3

import os


def get_path(*path_segments):
    return os.path.join(os.getcwd(), *path_segments)


def open_file(path_segments, mode, clean=False):
    file_path = get_path(*path_segments)
    if clean:
        open(file_path, 'w').close()
    return open(file_path, mode)


def main():
    readme = open_file(['README.rst'], 'a', clean=True)

    header = open_file(['README_header.rst'], 'r')
    configuration = open_file(['jfddns', 'rst', 'configuration.rst'], 'r')
    usage = open_file(['jfddns', 'rst', 'usage.rst'], 'r')

    for line in header.readlines():
        readme.write(str(line))

    readme.write('\n')

    for line in configuration.readlines():
        readme.write(str(line))

    readme.write('\n')

    for line in usage.readlines():
        readme.write(str(line))


if __name__ == '__main__':
    main()
