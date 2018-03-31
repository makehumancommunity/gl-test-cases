# gl-test-cases

Various short code snippets for testing OpenGL via PyQt5.

All these tests work via Qt5's opengl wrappers. It is important to note that this forces the OpenGL code to 
conform to OpenGL ES. For the most part the specific version is OpenGL ES 2.0.

## Running the tests

Before running the tests, you should add the root folder to PYTHONPATH so it can find the generic gl classes.
For example:

    export PYTHONPATH=`pwd`

## Existing test cases so far

* 00 *Does qt5 and the opengl canvas work at all?* - Launch a window with a canvas without doing any GL operations on it, just to see if things crash before even starting.
* 01 *Can the OpenGL functions be initialized?* - Launch a window with a canvas and try to create a GL "functions" object, but without actually doing anything with it.
* 02 *Can we change the background color?* - Try to use glClearColor and glClear() to change the background color to red. This is interesting in order to know if any operations whatsoever are allowed on the GL functions object. 

## Results

If you have run a test on your computer, please add information about a) what happened and b) what hardware/software specs you were running on

### 00 Does qt5 and the opengl canvas work at all?

* Ubuntu 16.04 /python 3.5.2 / nvidia: Works

### 01 Can the OpenGL functions be initialized?

* Ubuntu 16.04 /python 3.5.2 / nvidia: Works

### 02 Can we change the background color?

* Ubuntu 16.04 /python 3.5.2 / nvidia: Works

