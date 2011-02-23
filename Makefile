all:
	$(MAKE) all -C src
	$(MAKE) all -C test

install:
	$(MAKE) install -C src
	$(MAKE) install -C test

clean:
	$(MAKE) clean -C src
	$(MAKE) clean -C test

