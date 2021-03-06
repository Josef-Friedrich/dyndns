#! /usr/bin/env python3

import os


def get_path(*path_segments):
    return os.path.join(os.getcwd(), *path_segments)


def open_file(path_segments, mode, clean=False):
    file_path = get_path(*path_segments)
    if clean:
        open(file_path, 'w').close()
    return open(file_path, mode)

def read_rst_file(file_name, ):
    return open_file(['dyndns', 'rst', file_name], 'r')


def main():
    readme = open_file(['README.rst'], 'a', clean=True)
    header = open_file(['README_header.rst'], 'r')

    for line in header.readlines():
        readme.write(str(line))
    readme.write('\n')

    for rst_file in ['about.rst', 'installation.rst', 'configuration.rst',
                     'usage.rst']:
        rst = read_rst_file(rst_file)
        for line in rst.readlines():
            readme.write(str(line))
        readme.write('\n')


if __name__ == '__main__':
    main()
