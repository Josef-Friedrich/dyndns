from setuptools import setup, find_packages
import os
import versioneer


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="jfddns",
    author="Josef Friedrich",
    author_email="josef@friedrich.rocks",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A simple dynamic DNS update HTTP based API using python and the flask web framework.",
    long_description=read('README.rst'),
    url="https://github.com/Josef-Friedrich/jfddns",
    packages=find_packages(),
    install_requires=[
        'dnspython',
        'docutils',
        'flask',
        'PyYAML',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'jfddns-debug = jfddns:debug',
        ],
    },
    package_data = {
        '': ['*.rst', 'templates/*.html', 'static/*'],
    },
)
