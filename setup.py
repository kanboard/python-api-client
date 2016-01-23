from setuptools import setup

setup(
    name='kanboard',
    version='1.0.0',
    description='Kanboard API client',
    url='https://github.com/kanboard/kanboard-api-python',
    author='Frederic Guillot',
    author_email='fred@kanboard.net',
    license='MIT',
    packages=['kanboard'],
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ])
