from setuptools import setup, find_packages

setup(
    name='econ-datareader',
    version='0.2.2',
    description='Download Econ Data - Macro and Finance',
    author='WyChoi1995',
    author_email='wydanielchoi@gmail.com',
    url='https://github.com/WYChoi1995/econdatareader',
    install_requires=['pandas', 'aiohttp', 'nest_asyncio',],
    packages=find_packages(exclude=[]),
    keywords=['finance', 'econ'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)