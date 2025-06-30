from setuptools import setup, find_packages

setup(
    name='vctrl',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'vctrl = vctrl.cli:main'
        ],
    },
    install_requires=[],
)

