all:
	rm -f selenium_helper.xpi
	zip -x "*.xpi" -x "Makefile" -r selenium_helper.zip .
	mv selenium_helper.zip selenium_helper.xpi
