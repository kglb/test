from setuptools import setup, find_packages

setup(
    name="lab-management-system",
    version="1.0.0",
    description="一个基于Flask的课题组管理系统",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5",
        "Flask-Login==0.6.3",
        "Werkzeug==2.3.7",
        "python-dateutil==2.8.2",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)