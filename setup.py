import setuptools

def get_requirements():
    with open("requirements.txt") as requirements_file:
        lines = requirements_file.readlines()
        return [line.strip() for line in lines]

def get_packages(where):
    packages = setuptools.find_packages(where=where)
    packages_string = "\n".join(f"\t{package}" for package in packages)
    print(f"Packages found in '{where}':\n{packages_string}")
    return packages

setuptools.setup(
    name="selenium_helpers",
    version="1.0",
    author="Henri Immonen",
    author_email="henri.immonen@mostdigital.fi",
    install_requires=get_requirements(),
    packages=get_packages(where="src"),
    package_dir={"": "src"}
)
