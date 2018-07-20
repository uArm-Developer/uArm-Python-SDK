/* **************************************************************
* Software License Agreement (BSD License)
*
* Copyright (c) 2018, UFACTORY, Inc.
* All rights reserved.
*
* Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>
* ***************************************************************/

#include <Python.h>
#include <iostream>
#include <stdio.h>

using namespace std;

int main(int argc, char** argv)
{
    Py_Initialize();
    if (!Py_IsInitialized()) {
        return -1;
    }

    // exec the python code (at __main__)
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("import time");
    PyRun_SimpleString("sys.path.append('../..')");
    PyRun_SimpleString("from uarm import SwiftAPI");
    PyRun_SimpleString("swift = SwiftAPI()");
    PyRun_SimpleString("swift.waiting_ready()");
    PyRun_SimpleString("print(swift.get_device_info())");

    PyRun_SimpleString("swift.set_position(x=200, y=0, z=100, wait=True)");
    PyRun_SimpleString("print(swift.get_position())");


    // import the python module
    PyObject *pMod = PyImport_ImportModule("__main__");
    PyObject *pDict = PyModule_GetDict(pMod);
    // get the item from __main__
    PyObject *swift = PyDict_GetItemString(pDict, "swift");
    PyObject *result=  NULL;

    // call the method of swift with *args
    PyObject_CallMethod(swift, "set_position", "(i, i, i)", 200, -100, 150);
    PyObject_CallMethod(swift, "set_position", "(i, i, i)", 200, 100, 150);

    PyObject_CallMethod(swift, "set_position", "(i, i, i, i, i, i)", 200, 0, 150, 20000, 0, 1);

    result = PyObject_CallMethod(swift, "get_position", NULL, NULL);
    // handle the result
    if (PyList_Check(result)) {
        int i = 0;
        int size = PyList_Size(result);
        float pos[size];
        for (i = 0; i < size; i++) {
           PyObject *p = PyList_GetItem(result, i);
           PyArg_Parse(p, "f", &pos[i]);
           printf("%d: %f\n", i, pos[i]);
        }
    }

    Py_DECREF(result);
    Py_DECREF(swift);
    Py_DECREF(pDict);
    Py_DECREF(pMod);
    Py_Finalize();

    return 0;
}


