# -*- coding: utf-8 -*-
"""Installer for the jazkarta.easyformplugin.salesforce package."""

from setuptools import find_packages
from setuptools import setup
import sys


long_description = "\n\n".join(
    [
        open("README.md").read(),
        open("CHANGES.md").read(),
    ]
)

setup(
    name="jazkarta.easyformplugin.salesforce",
    version="1.0a1",
    description="Adds a behavior to collective.easyform to sync data to Salesforce",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Jazkarta",
    author_email="info@jazkarta.com",
    url="https://github.com/collective/jazkarta.easyformplugin.salesforce",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/jazkarta.easyformplugin.salesforce",
        "Source": "https://github.com/collective/jazkarta.easyformplugin.salesforce",
        "Tracker": "https://github.com/collective/jazkarta.easyformplugin.salesforce/issues",
        # 'Documentation': 'https://jazkarta.easyformplugin.salesforce.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["jazkarta", "jazkarta.easyformplugin"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    install_requires=[
        "setuptools",
        'Authlib<1; python_version<"3"',
        'simple-salesforce<1; python_version<"3"',
        "simple-salesforce",
        "collective.easyform",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            'vcrpy<4; python_version<"3"',
            "vcrpy",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = jazkarta.easyformplugin.salesforce.locales.update:update_locale
    """,
)
