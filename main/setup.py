import setuptools
import toml

# 
# get the data out of the toml file
# 
toml_info = toml.load("../pyproject.toml")
package_info = {**toml_info["tool"]["poetry"], **toml_info["tool"]["extra"]}

# 
# get the data out of the readme file
# 
with open("../README.md", "r") as file_handle:
    long_description = file_handle.read()

# 
# generate the project
#  
setuptools.setup(
    name=package_info["name"],
    version=package_info["version"],
    description=package_info["description"],
    url=package_info["url"],
    author=package_info["author"],
    author_email=package_info["author_email"],
    license=package_info["license"],
    packages=[package_info["name"]],
    install_requires=[
        # "ruamel.yaml", # tested on 0.17.21"
    ],
    classifiers=[
        # examples:
        # 'Development Status :: 5 - Production/Stable',
        # 'Intended Audience :: Developers',
        # 'Programming Language :: Python',
        # "Programming Language :: Python :: 3",
        # "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
)