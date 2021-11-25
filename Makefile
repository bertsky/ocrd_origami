PYTHON = python3
PIP = pip3
PYTHONIOENCODING=utf8

help:
	@echo
	@echo "  Targets"
	@echo
	@echo "    deps-ubuntu  Install only system dependencies"
	@echo "    origami      Clone subrepo"
	@echo "    deps         Install only Python deps via pip"
	@echo "    install      Install full Python package via pip"

deps-ubuntu:
	add-apt-repository ppa:alex-p/tesseract-ocr-devel # needs to be version 5
	add-apt-repository ppa:thopiekar/cgal # needs to be at least version 5
	apt-get update
	apt-get -y install git libffi-dev libcgal-dev tesseract
	# libnvinfer-dev libnvinfer-plugin-dev

origami:
	git submodule sync $@
	git submodule update --init $@
	sed -i s/scikit-geometry/skgeom/ $@/requirements/conda.txt
	echo 'h5py==2.10' >> $@/requirements/pip.txt

scikit-geometry:
	git clone https://github.com/scikit-geometry/scikit-geometry/

# Install Python deps via pip
deps: origami scikit-geometry
	$(PIP) install ./scikit-geometry # not available via pip, cf. #70
	$(PIP) install -r requirements.txt
	$(PIP) install -r origami/requirements/pip.txt
	$(PIP) install -r origami/requirements/conda.txt

# Install Python package via pip
install: origami
	$(PIP) install .

.PHONY: help deps-ubuntu deps install
