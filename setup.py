from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read()

setup(
    name="ulak-warden",
    version="0.0.1",
    author="Batuhan ÜNDAR",
    long_description=long_description,
    author_email="batuhan.undar@ulakhaberlesme.com.tr",
    packages=find_packages(),
    python_requires=">=3.7",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "warden=warden.__main__:main",
            "warden-configure=warden.configure:configure",
            "warden-logs=warden.configure:show_logs"
        ]
    },
    requirements=requirements
)
