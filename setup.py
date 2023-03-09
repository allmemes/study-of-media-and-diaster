from setuptools import setup, find_packages

setup(
    name="python-template",
    version="0.0.1",
    description="Python Template",
    author="Panda Pan",
    author_email="panchongdan@gmail.com",
    packages=find_packages(),
    install_requires=["pandas>=1.4.0"],  # some install requires example
    tests_require=["pytest>=3.3.1", "pytest-cov>=2.5.1"],
    python_requires=">=3.8",
)
