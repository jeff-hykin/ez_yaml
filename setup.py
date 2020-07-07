from setuptools import setup

setup(
    name='python-include',
    version='0.0.2',
    description="Path based import-all in Python, inspired by Ruby's include",
    url='https://github.com/jeff-hykin/python-include',
    author='Jeff Hykin',
    author_email='jeff.hykin@gmail.com',
    license='MIT',
    packages=['include'],
    install_requires=[],
    test_suite='tests',
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ]
)
