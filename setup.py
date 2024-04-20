   
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup 
 
# with open("README.md", "rb") as f:
#     long_descr = f.read().decode("utf-8")
 
 
setup(
    name = "HadesMapper",
    packages = ["HadesMapper"],
    entry_points = {
        "console_scripts": ['HadesMapper = HadesMapper.cli:main']
        },
    version = "2.0",
    description = "Unpack Hades and Hades II's map binaries into JSON and pack JSON into game usable map binaries",
    #long_description = long_descr,
    author = "erumi321",
    author_email = "erumi321@gmail.com",
    url = "",
    )