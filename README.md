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

## Results

If you have run a test on your computer, please add information about a) what happened and b) what hardware/software specs you were running on

### 00 Does qt5 and the opengl canvas work at all?

To be written

