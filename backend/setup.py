from setuptools import setup, find_packages

setup(
    name="engineering-design-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "openai",
        "python-dotenv",
        "pydantic",
        "pydantic-settings>=2.0.0",
        "fastapi-cors",
        "pyautogen>=0.2.0"
    ]
) 