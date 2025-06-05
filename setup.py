from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="youtube-py2",
    version="1.0.0",
    author="Chihalu",
    description="A simplified wrapper for YouTube Data API v3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "google-api-python-client>=2.0.0",
    ],
    keywords="youtube api wrapper python",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/youtube-py2/issues",
        "Source": "https://github.com/yourusername/youtube-py2",
    },
)
