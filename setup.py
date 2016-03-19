from setuptools import setup, find_packages

setup(
    name="spotd",
    version="0.0.1",
    description=("Stop before your server does."),
    license="MIT",
    keywords="aws, spot instances, systemd",
    url="https://github.com/grahamc/spotd",
    packages=find_packages(),
    install_requires=[
    ],
    test_suite='test'
)
