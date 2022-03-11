import ez_yaml

value = ez_yaml.to_object(file_path="./tests/info.yaml")
print(f'''value = {value}''')

value = ez_yaml.to_object(file_path="./tests/info.yaml", load_nested_yaml=True)
print(f'''value = {value}''')