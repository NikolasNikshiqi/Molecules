# Molecules

Program allows users to upload sdf files and view their molecule models on a web browser.

Once ran it creates an empty SQL database called molecules.db where all the important information is stored. If the database already exists
then it does not create a new one it simply connects with the existing one.

* Compiling and running
To compile the code first you need to run this command inside the folder of the source code: export LD_LIBRARY_PATH="$(pwd)"
Then you need to run the command make. After compilation is complete all you need to do is run the server.py file.
To access the webserver you will need to write one of these in your browser: http://127.0.0.1:57237 or http://localhost:57237

* This code can only work on linux machines since the libraries needed to compile the code have been specified with their linux paths in the make file.
If you need to make it work on a different OS, simply change the path of these libraries to the preferred ones.
