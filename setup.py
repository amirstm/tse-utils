import setuptools

setuptools.setup(
    name="tse_utils",
    version="0.0.3",
    author="Arka Equities & Securities",
    author_email="info@arkaequities.com",
    description="General utilities used for data mining in Tehran Stock Exchange (TSE).",
    packages=setuptools.find_packages(),
    install_requires=["httpx", "beautifulsoup4", "lxml"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
