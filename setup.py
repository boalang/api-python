import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boa-api",
    version="0.1.14",
    author="Boa Project",
    author_email="boasupport@iastate.edu",
    description="Client API for using the Boa infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boalang/api-python",
    packages=setuptools.find_packages(),
    package_data={package: ["py.typed", "*.pyi", "**/*.pyi"] for package in setuptools.find_packages()},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
