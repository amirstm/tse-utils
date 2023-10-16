"""Building the library"""
import setuptools

setuptools.setup(
    name="tse_utils",
    version="1.0.4",
    author="Arka Equities & Securities",
    author_email="info@arkaequities.com",
    description="General utilities used for data mining in Tehran Stock Exchange (TSE).",
    long_description="Utilities for data mining and auto-trading in Tehran Stock Exhchange. \
        Contains TSETMC API implementation and other useful interfaces for securities market \
        data catching and processing.",
    packages=setuptools.find_packages(),
    install_requires=["httpx", "beautifulsoup4", "lxml"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
