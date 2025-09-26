from setuptools import setup, find_packages

setup(
    name="pyPhyNR",
    version="0.1.0",
    description="Python toolkit for 5G NR physical layer simulations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="kir812",
    author_email="kir812@gmail.com",
    url="https://github.com/kir812/pyPhyNR",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "ipykernel",
        "jupyter",
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'flake8',
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
    ],
    keywords="5G NR, physical layer, telecommunications, signal processing",
) 