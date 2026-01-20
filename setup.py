from setuptools import find_packages, setup

setup(
    name="gradio-terminal",
    version="1.1.0",
    author="Po-Hsuan Huang",
    author_email="aben20807@gmail.com",
    description="A Gradio component that provides a fully functional terminal using xterm.js and PTY",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    license="Apache-2.0",
    install_requires=[
        "gradio>=6.3.0",
        "flask>=3.1.2",
        "flask-socketio>=5.6.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
