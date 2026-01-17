from setuptools import setup, find_packages

setup(
    name="agentic-sdlc",
    version="2.1.0",
    packages=find_packages(include=['agentic_sdlc', 'agentic_sdlc.*']),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        'console_scripts': [
            'agentic-sdlc=agentic_sdlc.cli:main',
            'asdlc=agentic_sdlc.cli:main',
        ],
    },
    author="Dao Quang Truong",
    author_email="truongnat@gmail.com",
    description="AI-powered SDLC framework with self-learning brain",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/truongnat/agentic-sdlc",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
)
