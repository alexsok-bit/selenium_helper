all:
	rm -f selenium_helper.xpi
	zip -i "data/*" -i "_locales/*" -i "icon.png" -i "manifest.json" -i "README.md" -r selenium_helper.zip .
	mv selenium_helper.zip selenium_helper.xpi
