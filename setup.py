from setuptools import setup

setup(
    name='ralogs',
    version='1.3',
    url='https://github.com/barell/ralogs',
    packages=['ralogs',],
    license='MIT',
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'ralogs=ralogs.ralogs:main'
        ]
    },
    install_requires=['requests', 'aiohttp'],
)