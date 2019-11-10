from setuptools import setup, find_packages


with open("requirements.txt") as f:
    REQUIREMENTS = f.readlines()

with open("README.md") as f:
    README = f.read()


setup(
    name="privacy.py",
    author="FasterSpeeding",
    url="https://github.com/FasterSpeeding/privacy.py",
    version="",
    packages=find_packages(),
    license="BSD",
    description="A Python lib for Privacy.com",
    long_description=README,
    include_package_data=True,
    install_requires=REQUIREMENTS,
    setup_requires=['pytest-runner'],
    test_suite="pytest",
    tests_require=[
        "pytest==5.2.2"
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ])
