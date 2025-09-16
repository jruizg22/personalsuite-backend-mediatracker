from setuptools import setup, find_packages

setup(
    name='media_tracker',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'sqlmodel'
    ],
    entry_points={
        'personal_suite.modules': [
            'media_tracker = media_tracker.module:Module'
        ]
    }
)