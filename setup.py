from setuptools import setup, find_packages

import os

def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as handle:
        return handle.read()

setup(
    name='wp_title',
    version='0.1.0',
    author='NTL',
    author_email='justdont@example.com',
    description='Python script for naming TV seasons using Wikipedia data',
    license='BSD',
    install_requires=['wikipedia'],
    keywords='wikipedia television tv',
    url='https://github.com/ntlimited/wp-title',
    packages=['wp_title'],
    long_description=readme(),
    classifiers=[],
    
    entry_points={
        'console_scripts': [
            'wp-title = wp_title:bootstrap',
        ],
        'setuptools.installation': [
            'eggsecutable = wp_title:bootstrap',
        ],
    },
)
