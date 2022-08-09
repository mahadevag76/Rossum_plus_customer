build:
	 /bin/python3 setup.py build_ext --inplace
	 mv sample_customer_code.py backup_file
	 /bin/python3 sample_runner.py --name Mahadeva
clean:
	rm -rf __pycache__
	rm -rf build
	rm -rf sample_customer_code.cpython-38-x86_64-linux-gnu.so
	rm -rf sample_customer_code.c
	mv  backup_file sample_customer_code.py
install : 
	pip3 install cython
	pip3 install setuptools

