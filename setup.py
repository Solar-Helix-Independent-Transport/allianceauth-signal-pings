import os 
from setuptools import find_packages, setup

from signalpings import __version__

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='allianceauth-signal-pings',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Pings for Signals!',
    long_description=README,
    long_description_content_type='text/markdown', 
    url='https://github.com/pvyParts/allianceauth-signal-pings',
    author='Aaron Kable',
    author_email='aaronkable@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',        
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)