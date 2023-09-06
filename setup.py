from setuptools import setup, find_packages

setup(
    name="apitoolkit_flask",
    version="0.1",
    packages=find_packages(),
    description='A Flask SDK for Apitoolkit integration',
    author_email='hello@apitoolkit.io',
    author='APIToolkit',
    install_requires=[
        'Flask',
        'requests',
        'google-cloud-pubsub',
        'google-auth',
    ],
)
