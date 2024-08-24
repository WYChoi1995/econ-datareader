from setuptools import setup, find_packages

with open('readme.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='econ-datareader',
    version='0.2.3',
    description='Download Econ Data - Macro and Finance',
    long_description=long_description,
    long_description_content_type='text/markdown',
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