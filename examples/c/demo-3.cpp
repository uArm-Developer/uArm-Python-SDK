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

    // exec the python code
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('../..')");

    // import the module (from uarm import SwiftAPI)
    PyObject *pMod = PyImport_ImportModule("uarm");
    PyObject *pDict = PyModule_GetDict(pMod);
    PyObject *pClass = PyDict_GetItemString(pDict, "SwiftAPI");
    // call the object (swift = SwiftAPI())
    PyObject *swift = PyObject_CallObject(pClass, NULL);

    // call the method of swift (swift.waiting_ready())
    PyObject_CallMethod(swift, "waiting_ready", NULL, NULL);


    PyObject *result=  NULL;

    // get the method of swift
    PyObject *func = PyObject_GetAttrString(swift, "set_position");
    // generate the dict
    PyObject *kw = PyDict_New();
    PyDict_SetItemString(kw, "x", Py_BuildValue("i", 200));
    PyDict_SetItemString(kw, "y", Py_BuildValue("i", 0));
    PyDict_SetItemString(kw, "z", Py_BuildValue("i", 100));
    PyDict_SetItemString(kw, "wait", Py_BuildValue("i", 1));

    // call the method of swift with **kwargs
    result = PyObject_Call(func, PyTuple_New(0), kw);

    // call the method of swift with *args
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
    Py_DECREF(kw);
    Py_DECREF(func);
    Py_DECREF(swift);
    Py_DECREF(pClass);
    Py_DECREF(pDict);
    Py_DECREF(pMod);
    Py_Finalize();

    return 0;
}
