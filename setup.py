from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='polymaze',
    version='0.6.91',
    description='Create polygon-tesselation mazes from a variety of sources.',
    long_description=long_description,
    url='https://github.com/kobejohn/polymaze',
    author='John Nieri',
    author_email='niericentral@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Artistic Software',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='mazes tesselation',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['PILLOW'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'polymaze=polymaze.cli:commandline'
        ]
    }
)
