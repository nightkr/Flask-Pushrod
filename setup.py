from setuptools import setup


setup(
    name='Flask-Pushrod',
    version='0.1-dev',
    url='http://github.com/dontcare4free/flask-pushrod',
    license='MIT',
    author='Nullable',
    author_email='teo@nullable.se',
    description='An API microframework based on the idea of that the UI is just yet another endpoint',
    packages=['flask_pushrod', 'flask_pushrod.renderers'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Werkzeug>=0.7',
        'Flask>=0.9',
    ],
    tests_require=[
        'nose==1.2.1',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector',
)
