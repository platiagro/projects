from setuptools import find_packages, setup

from projects import __version__

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

extras = {
    "testing": [
        "pytest>=4.4.0",
        "pytest-xdist==1.31.0",
        "pytest-cov==2.8.1",
        "flake8==3.7.9",
    ]
}

setup(
    name="projects",
    version=__version__,
    author="Fabio Beranizo Lopes",
    author_email="fabio.beranizo@gmail.com",
    description="Manages projects.",
    license="Apache",
    url="https://github.com/platiagro/projects",
    packages=find_packages(),
    package_data={
        "projects": ["config/*.ipynb"],
    },
    install_requires=requirements,
    extras_require=extras,
    python_requires=">=3.6.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "platiagro-init-db = projects.database:init_db",
        ]
    },
)