from setuptools import setup

setup(
    name='PyGithubFork',
    version='0.0.0',
    description='Code wraps PyGithub to simplify workflows dealing with forks',
    author='hassenius',
    url='https://github.com/multicloud-ops/PyGithubFork',
    packages=['githubfork'],
    install_requires=[
        'pygithub'
    ]
)
