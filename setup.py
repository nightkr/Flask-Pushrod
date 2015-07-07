from setuptools import setup
from setuptools.command.test import test as TestCommand

from os import path


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--verbose', '-s']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        raise SystemExit(pytest.main(self.test_args))


setup(
    name='Flask-Pushrod',
    version='0.2.dev',
    url='http://github.com/opyate/flask-pushrod',
    license='MIT',
    author='Juan Uys',
    author_email='opyate+flaskpushrod@gmail.com',
    description='Views for your API',
    long_description=open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')).read(),
    packages=['flask_pushrod', 'flask_pushrod.renderers'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Werkzeug>=0.7',
        'Flask>=0.10.1',
        'future'
    ],
    tests_require=[
        'pytest>=2.2.4',
        'nose>=1.2.1',

        # For example
        'sqlalchemy>=0.7.9',
        'flask-sqlalchemy>=0.16',
    ],
    cmdclass={'test': PyTest},
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
)
