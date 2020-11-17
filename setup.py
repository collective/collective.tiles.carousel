# -*- coding: utf-8 -*-
"""Installer for the collective.tiles.bootstrapslider package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='collective.tiles.bootstrapslider',
    version='1.0a1',
    description="Slider for plone.app.mosaic based on Bootstrap 5",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS',
    author='Peter Holzer',
    author_email='peter.holzer@agitator.com',
    url='https://github.com/collective/collective.tiles.bootstrapslider',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/collective.tiles.bootstrapslider',
        'Source': 'https://github.com/collective/collective.tiles.bootstrapslider',
        'Tracker': 'https://github.com/collective/collective.tiles.bootstrapslider/issues',
        # 'Documentation': 'https://collective.tiles.bootstrapslider.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.tiles'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==3.8",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'Products.CMFPlone',
        'plone.restapi',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = collective.tiles.bootstrapslider.locales.update:update_locale
    """,
)
