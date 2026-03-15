from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="MastoCloud",  # Package name
    version="0.1.0",    # Initial release version
    author="Vincent Willcox",
    author_email="talking@talktech.info",
    description="A tool to create a Wordcloud from your Mastodon Toots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vwillcox/MastoCloud",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust if different
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.6',  # Specify your Python version requirement
    install_requires=[
        # List your dependencies here
        # 'requests>=2.25.1',
        # 'some_other_package>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'mastocloud=mastocloud.main:main',  # Adjust based on your entry point
        ],
    },
    include_package_data=True,
)
