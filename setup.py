from setuptools import setup, find_packages

setup(
    name="jfddns",
    version="0.0.1",
    author="Josef Friedrich",
    author_email="josef@friedrich.rocks",
    description="Simple dynamic ddns update tool using HTTP",
    url="https://github.com/Josef-Friedrich/jfddns",
    packages=find_packages(),
    install_requires=[
        'dnspython',
        'flask',
        'PyYAML',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points = {
        'console_scripts': [
            'jfddns = jfddns:main',
        ],
    },
)
