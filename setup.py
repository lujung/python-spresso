import os

from setuptools import setup

setup(
    name="python-spresso",
    version=open(".version").read(),
    description="SPRESSO providers for python",
    long_description=open("README.rst").read(),
    author="Lukas Jung",
    author_email="mail@lukasjung.de",
    url="https://github.com/lujung/python-spresso",
    download_url="https://github.com/lujung/python-spresso/archive/master.tar.gz",
    packages=[d[0].replace("/", ".") for d in os.walk("spresso") if
              not d[0].endswith("__pycache__")],
    install_requires=[
        'cryptography',
        'requests',
        'requests[socks]',
        'Jinja2',
        'jsonschema'
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
    ]
)
