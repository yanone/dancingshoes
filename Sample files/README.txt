My preferred setup:

myFP.features
=============
Your actual feature development goes here. Should be the same for all your fonts and font development applications.
Install myFP (my font production) as a python library on your system, possibly in a fixed path in your home folder, so you can back it up and easily access. Create a .pth file in python's site-packages folder that points to myFP. Make sure that file exists for all versions of python you may want to use (2.3 for FontLab Studio 5, 2.6 etc.)
http://docs.python.org/library/site.html

Make sure that the path to substitutions.csv in features.py point to the correct location in your folder structure.


Access it from outside
======================
Then you create scripts for each application, be it FontLab, RoboFont or Glyphs or command line, to access myFP.features. 
See MakeFeatures_RoboFab.py and MakeFeatures_FontLab.py for examples.
