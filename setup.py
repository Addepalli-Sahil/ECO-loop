from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eco-loop-building-agents",
    version="0.1.0",
    author="Eco-Loop Team",
    author_email="team@ecoloop.ai",
    description="Autonomous AI-driven building management system using EnergyPlus and LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/eco-loop-building-agents",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=[
        "energyplus>=23.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "langchain>=0.1.0",
        "pydantic>=2.4.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "matplotlib>=3.8.0",
        "plotly>=5.17.0",
        "streamlit>=1.28.0",
        "pytest>=7.4.0",
    ],
)
