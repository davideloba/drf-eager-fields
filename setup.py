# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
from setuptools import setup


def readme():
    with open("README.md", "r") as file:
        return file.read()

setup(
    name='drf_eager_fields',
    version='0.0.1',
    description='Eager load fields dynamically requested for Django REST Framework',
    long_description=readme(),
    author='Davide Loba',
    url='https://github.com/davideloba/drf-eager-fields.git',
    packages=['drf_eager_fields'],
    license='MIT',
)
