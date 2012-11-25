.PHONY: all clean

all:
	$(MAKE) clean
	$(MAKE) compile
	python ./MainView.py

clean:
	powershell /C rm *.pyc, */*.pyc, ../*/*.pyc

compile:
	pyrcc4 -py2 qrc.qrc > resources.py

debug-html:
	$(MAKE) compile
	python ./MainView.py > file.html