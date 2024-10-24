from setuptools import setup, find_packages

setup(
    name="git2text",
    version="0.1",
    description="A utility to extract and format a codebase into Markdown format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Marcelo Rauter",
    author_email="marcelorauter2@gmail.com",
    url="https://github.com/mrauter1/git2text",
    packages=find_packages(where="src"),  # Looks for Python packages in the 'src' directory
    package_dir={"": "src"},  # Specifies that the root package is located in 'src'
    py_modules=['git2text'],  # Since git2text.py is directly under src, we treat it as a module
    install_requires=[
        'pathspec',
    ],
    entry_points={
        'console_scripts': [
            'git2text=git2text:main',  # Points to 'main' inside git2text.py
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
