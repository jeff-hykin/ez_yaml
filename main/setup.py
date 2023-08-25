import setuptools
import toml
from file_system_py import iterate_paths_in

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
    package_data={
        # include all files/folders in the module (recursively)
        package_info["name"]: [
            each[len(package_info["name"])+1:]
                for each in iterate_paths_in(package_info["name"], recursively=True)
                    if (
                        not each.endswith(".pyc")
                        and not each.endswith("/.keep")
                        and not each.endswith('.canonical')
                        and not each.endswith('.data')
                        and not each.endswith('.error')
                        and not each.endswith('.skip-ext')
                        and ('/settings/' not in each)
                        and ('/commands/' not in each)
                        and ('/documentation/' not in each)
                    )
        ],
    },
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