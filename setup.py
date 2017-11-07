from setuptools import setup
from codecs import open
from os import path
from gigantumcli import __version__

# to update
# python setup.py sdist bdist_wheel
# twine upload --skip-existing dist/*

cwd = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(cwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies
with open(path.join(cwd, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.read().split('\n')

setup(
    name='gigantum',
    version=__version__,

    description='CLI for the Gigantum Platform',
    long_description=long_description,

    install_requires=install_requires,

    author='Gigantum/FlashX, LLC',
    author_email='hello@gigantum.io',

    entry_points={
        'console_scripts': ['gigantum=gigantumcli.cli:main'],
    },
    packages=['gigantumcli'],
    include_package_data=True,

    url='https://github.com/gigantum/gigantum-cli',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
    ],
    keywords=[
        'data-science',
        'science',
        'gigantum',
        'open-science'
    ]
)
