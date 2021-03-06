from setuptools import setup, find_packages


setup(
    name='mdf_refinery',
    version='0.1.0',
    packages=find_packages(),
    description='Materials Data Facility python package',
    install_requires=[
        "mdf_forge>=0.4.4",
        "mdf_toolbox>=0.1.3",
        "crossrefapi>=1.2.0",
        "globus-sdk>=1.1.1",
        "requests>=2.18.1",
        "python-magic>=0.4.13",
        "pandas>=0.20.3",
        "tqdm>=4.14.0",
        "ase>=3.14.1",
        "beautifulsoup4>=4.6.0",
        "xmltodict>=0.10.2",
        "pymatgen>=2017.6.8",
        "jsonschema>=2.6.0",
        "pymongo>=3.4.0",  # For bson.ObjectId
        "Pillow>=3.1.2"
    ],
    package_data={'mdf_refinery': ['schemas/*.schema']}
)
