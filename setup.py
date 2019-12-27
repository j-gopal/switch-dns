from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="switch-dns",
    version="1.0.0",
    description="For directly setting the DNS servers being used on your machine.",
    long_description=readme,
    author="Joshua R. Gopal",
    url="https://github.com/j-gopal/switch-dns",
    license="MIT",
    install_requires=["docopt==0.6.2"],
    python_requires=">=3.6"
)
