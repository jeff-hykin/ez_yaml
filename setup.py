from setuptools import setup

setup(
    name='ez_yaml',
    version='1.0.0',
    description="Straighforward wrapper around Ruamel Yaml",
    url='https://github.com/jeff-hykin/ez_yaml',
    author='Jeff Hykin',
    author_email='jeff.hykin@gmail.com',
    license='MIT',
    packages=['ez_yaml'],
    install_requires=[
        "ruamel.yaml"
    ],
    test_suite='tests',
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ]
)
