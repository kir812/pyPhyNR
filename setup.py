from setuptools import setup, find_packages

setup(
    name="pyPhyNR",
    version="0.1.0",
    description="Python toolkit for 5G NR physical layer simulations",
    author="Your Name",
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
) 