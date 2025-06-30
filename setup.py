from setuptools import setup, find_packages

setup(
    name='vctrl',
    version='0.1',
    packages=find_packages(),  
    py_modules=['cli'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'vctrl=cli:main'
        ],
    },
)

