from setuptools import setup

import os, sys, moss

with open("README.md", "r", encoding = "UTF-8") as file:
    long_desc = file.read()

with open("requirements.txt", "w", encoding = "UTF-8") as file:
    file.write("\n".join(moss.__requirements__))

setup(
    name = "moss-engine",
    packages = ["moss"],
    version = moss.__version__,
    entry_points = {
        "console_scripts": [
            "moss-editor = moss.editor:main",
            "moss-run = moss.project:main"
        ]
    },
    description = long_desc.split("\n")[1],
    long_description = long_desc,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Aermoss/Moss",
    author = "Yusuf Rençber",
    author_email = "aermoss.0@gmail.com",
    license = "MIT",
    keywords = [],
    include_package_data = True,
    install_requires = moss.__requirements__
)