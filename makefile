CC = gcc
SWIG = swig
CFLAGS = -std=c99 -pedantic  -Wall -fpic
LIBS = -lmol -lpython3.7m

PYTHON_INCLUDE = /usr/include/python3.7m/
PYTHON_LIBDIR = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

all: libmol.so molecule_wrap.o _molecule.so
	
mol.o: mol.c
	$(CC) $(CFLAGS) -c mol.c

libmol.so: mol.o
	export LD_LIBRARY_PATH="$(pwd)"
	$(CC) mol.o -shared -o libmol.so

molecule_wrap.c: molecule.i
	$(SWIG) -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -I$(PYTHON_INCLUDE) -c molecule_wrap.c -o molecule_wrap.o

_molecule.so: molecule_wrap.o
	$(CC) -shared -dynamiclib -L$(PYTHON_LIBDIR) -L. $(LIBS) -o _molecule.so molecule_wrap.o 

clean:
	rm -f *.o *.so molecule_wrap.c *_wrap.* *_wrap.c *.pyc *.pyo


