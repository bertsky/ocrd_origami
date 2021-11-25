"""
Installs:
    - origami-batch-1-segment
    - origami-batch-2-contours
    - origami-batch-3-flow
    - origami-batch-4-dewarp
    - origami-batch-5-layout
    - origami-batch-6-lines
    - origami-batch-7-order
    - origami-batch-8-ocr
    - origami-batch-9-compose
    - ocrd-origami-segment
    - ocrd-origami-deskew (not yet)
    - ocrd-origami-dewarp (not yet)
"""

import codecs
import json
from setuptools import setup, find_packages

def get_description(path):
    with codecs.open(path, encoding='utf-8') as f:
        return f.read()

def get_version(path):
    with open(path, 'r') as f:
        return json.load(f)['version']

def get_requirements(*paths):
    pkgs = list()
    for path in paths:
        pkgs.extend(open(path).read().strip().split('\n'))
    return pkgs

setup(
    name='ocrd_origami',
    version=get_version('./ocrd-tool.json'),
    description='OCR-D wrapper for poke1024/origami OLR+OCR',
    long_description=get_description('README.md'),
    long_description_content_type='text/markdown',
    author='Robert Sachunsky',
    author_email='sachunsky@informatik.uni-leipzig.de',
    url='https://github.com/bertsky/ocrd_origami',
    license='Apache License 2.0',
    package_dir={'': '.',
                 'origami': './origami/origami'},
    packages=find_packages(where='./origami') + find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=get_requirements('requirements.txt',
                                      'origami/requirements/pip.txt',
                                      'origami/requirements/conda.txt'),
    package_data={
        '': ['*.json', '*.yml', '*.yaml', '*.csv.gz', '*.jar', '*.zip'],
    },
    entry_points={
        'console_scripts': [
            'origami-batch-1-segment=origami.batch.detect.segment:segment',
            'origami-batch-2-contours=origami.batch.detect.contours:extract_contours',
            'origami-batch-3-flow=origami.batch.detect.flow:detect_flow',
            'origami-batch-4-dewarp=origami.batch.detect.dewarp:dewarp',
            'origami-batch-5-layout=origami.batch.detect.layout:detect_layout',
            'origami-batch-6-lines=origami.batch.detect.lines:detect_lines',
            'origami-batch-7-order=origami.batch.detect.order:reading_order',
            'origami-batch-8-ocr=origami.batch.detect.ocr:run_ocr',
            'origami-batch-9-compose=origami.batch.detect.compose:compose',
            'ocrd-origami-segment=ocrd_origami.cli:ocrd_origami_segment',
        ]
    },
)
