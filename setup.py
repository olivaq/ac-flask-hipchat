"""
AC-Flask-HipChat
-------------

A library to help write a Flask-based HipChat add-on
"""
from setuptools import setup


setup(
    name='AC-Flask-HipChat',
    version='0.2.1.dev0',
    url='https://bitbucket.org/atlassianlabs/ac-flask-hipchat',
    license='APLv2',
    author='Don Brown',
    author_email='mrdon@twdata.org',
    description='Atlassian Connect library based on Flask for HipChat',
    long_description=__doc__,
    packages=['ac_flask', 'ac_flask.hipchat'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'pymongo',
        'redis',
        'requests',
        'PyJWT'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
