import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as readme_file:
    README = readme_file.read()

setup(
    name='k8s-workload-scaler',
    version='0.0.2',
    packages=['k8s_workload_scaler'],
    url='github.com/eminaktas/k8s-workload-scaler',
    license='MIT',
    author='emin.aktas',
    author_email='eminaktas34@gmail.com',
    description='Kubernetes workload scaler',
    long_description=README,
    install_requires=[
        'setuptools~=54.2.0',
        'kubernetes~=12.0.1',
        'requests~=2.25.1',
        'prometheus-api-client~=0.4.2',
    ]
)
