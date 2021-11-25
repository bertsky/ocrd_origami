# ocrd_origami

    OCR-D wrapper for poke1024/origami OLR+OCR

  * [Introduction](#introduction)
  * [Installation](#installation)
  * [Usage](#usage)
     * [OCR-D processor interface ocrd-origami-segment](#ocr-d-processor-interface-ocrd-origami-segment)
  * [Testing](#testing)


## Introduction

This offers [OCR-D](https://ocr-d.de) compliant [workspace processors](https://ocr-d.de/en/spec/cli) for
[Origami](https://github.com/poke1024/origami), the document image processing suite for historical newspapers.

... WORK IN PROGRESS ...

## Installation

First install system dependencies:

    sudo make deps-ubuntu

(Besides Python>=3.7 you'll need at least `libffi-dev`, `libcgal-dev` and `git`, plus a recent `tesseract`.)

Now clone the subrepository, if you have not already:

    make origami

Which is the equivalent of:

    git submodule update --init origami

Create and activate a [virtual environment](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments) as usual.

To install Python dependencies:

    make deps

Which is the equivalent of:

    pip install -r requirements.txt
    pip install -r origami/requirements/pip.txt
    pip install -r origami/requirements/conda.txt

To install this module, do:

    make install

Which is the equivalent of:

    pip install .

## Usage

### [OCR-D processor](https://ocr-d.de/en/spec/cli) interface `ocrd-origami-segment`

To be used with [PAGE-XML](https://github.com/PRImA-Research-Lab/PAGE-XML) documents in an [OCR-D](https://ocr-d.de/en/about) annotation workflow.

```
... SHOW OCRD CLI HERE...
```

## Testing

(not yet)
