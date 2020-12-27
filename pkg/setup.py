from setuptools import setup, find_packages

setup(
    name='dockerfile-parser',
    keywords='docker dockerfile parser parsing',
    version='0.0.2',
    url='https://github.com/eg0r/dockerfile-parser',
    license='MIT',
    author='Egor Smolyakov',
    author_email='egorsmkv@gmail.com',
    description='Library for parsing Dockerfile.',
    zip_safe=False,
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
