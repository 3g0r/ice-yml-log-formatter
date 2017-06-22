from setuptools import find_packages, setup

setup(
    name='ice-yml-log-formatter',
    packages=['ice_yml_log_formatter'],
    version='0.1.0',
    description='ZeroC Ice logging utils',
    author='3g0r',
    author_email='eg0r.n1k0l43v@gmail.com',
    url='https://github.com/3g0r/ice-yml-log-formatter',
    keywords=['ice', 'yml', 'log'],
    classifiers=[],
    long_description=open('README.rst').read(),
    license='MIT',
    install_requires=[
        'PyYAML==3.12',
        'zeroc-ice==3.6.3'
    ],
    include_package_data=True,
    package_data={'': ['README.rst']},
)
