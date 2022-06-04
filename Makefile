IN := $(wildcard config/*.yaml)

all: $(patsubst config/%.yaml,%.3mf,$(IN))
clean:
	rm -Rf *.scad *.3mf

.PHONY: all clean

%.scad: config/%.yaml
	/usr/bin/env python3 incubator.py -o $@ -c $<

%.3mf: %.scad
	/usr/bin/env openscad --export-format 3mf -o $@ $<
