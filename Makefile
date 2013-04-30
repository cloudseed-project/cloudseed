bootstrap: clean
	python setup.py sdist
	mv dist/$(shell python setup.py --fullname).tar.gz sample/.cloudseed/current/states
clean:
	rm -rf dist
