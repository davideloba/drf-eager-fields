# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
# https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56

from setuptools import setup


def readme():
    with open("README.md", "r") as file:
        return file.read()


setup(
    name="drf_eager_fields",
    packages=["drf_eager_fields"],
    version="0.0.3",
    license="MIT",
    description="Eager load fields dynamically requested for Django REST Framework",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Davide Loba",
    url="https://github.com/davideloba/drf-eager-fields.git",
    keywords=["eager", "dynamic", "drf", "serializer"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
