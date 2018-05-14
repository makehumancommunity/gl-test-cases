# gl-test-cases

Various short code snippets for testing OpenGL ES via PyQt5.

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
* 03 *Can we compile shaders?* - Since everything in GLES seems to require shaders, check if we can create a shader program with vertex and fragment shaders.
* 04 *Draw a dot (hardcoded)* - Try to draw a 10 pixel large red dot on a black background. Note that point size, location (center screen) and color are controlled in the shaders, not in the python source. 
* 05 *Draw a dot (dynamic)* - Try to draw a 10 pixel large red dot on a black background. Control location (upwardish, rightish) with shader attributes from inside python.
* 06 *Use an array buffer to draw dots* - Set up a buffer array containing vertex data for for vertices, tie the buffer to the shader attribute, and use this approach to draw dots at the vertex positions. 
* 07 *Use an array buffer to draw a triangle* - Set up a buffer array containing vertex data, tie the buffer to the shader attribute, and use this approach to draw a triangle connecting the vertex positions. 
* 08 *Use an array buffer to draw a quad* - Set up a buffer array containing vertex data, tie the buffer to the shader attribute, and use this approach to draw a quad connecting the vertex positions. 
* 09 *Mix position and color data in one array* - Set up a buffer array containing both position data and color data, and use this approach to draw a multicolored quad. 
* 10 *Scale according to window size* - Use a "uniform" in the vertex shader to scale to compensate for window size. 
* 11 *Rotate the quad* - Use a "uniform" in the vertex shader to rotate the drawn quad. 
* 12 *Mouse rotation* - Draw a quad and implement mouse rotation to be able to rotate it. Since there is no perspective nor lighting yet, it might not look overly impressing. 
* 13 *Draw two triangles using Qt's wrappers* - Use Qt's VAO and VBO wrappers to draw two separate triangles. 

## Results

If you have run a test on your computer, please add information about a) what happened and b) what hardware/software specs you were running on

### 00 Does qt5 and the opengl canvas work at all?

* Ubuntu 16.04 /python 3.5.2 / nvidia: Works

### 01 Can the OpenGL functions be initialized?

* Ubuntu 16.04 /python 3.5.2 / nvidia: Works

### 02 Can we change the background color?

* Ubuntu 16.04 /python 3.5.2 / nvidia: Works

### 03 Can we compile shaders?

* Ubuntu 16.04 /python 3.5.2 / nvidia: Works

### 04 Draw a dot (hardcoded)

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 05 Draw a dot (dynamic)

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 06 Use an array buffer to draw dots

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 07 Use an array buffer to draw a triangle

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 08 Use an array buffer to draw a quad

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 09 Mix position and color data in one array

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 10 Scale according to window size

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 11 Rotate the quad

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 12 Mouse rotation

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works

### 13 Draw two triangles using Qt's wrappers

* Ubuntu 16.04 / anaconda python 3.6.5 / nvidia: Works


