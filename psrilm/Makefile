PYREXC=pyrexc
PYTHON=python2.4

%.c: %.pyx
	$(PYREXC) $< -o $@

%.cc: %.pyx
	$(PYREXC) $< -o $@

all: srilm.c
	$(PYTHON) setup.py build

clean:
	rm -rf build srilm.so
