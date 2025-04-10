best practices for running tests within pycharm and having imports of scripts
and modules from src work correctly seems to be this:

src
  __init__.py
    this init file is empty
test
  __init__.py
       this init file loads src directory into the system path
       Note that this implies that unit tests are run with a working
       directory being the project base directory.
       import os
       import sys
       parent_dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
       sys.path.append(parent_dir_name + "/src")
       print(sys.path)

problems can occur when the run configs in pycharm have a working directory other
than the base project directory.  this can happen if the first time a test is run is from
the right click context menu on the test file name.  if that is the case, open the
configuration with Run -> Edit Configurations then select the test file rom the left
menu then edit the working directory to be the base directory.

Note that the command line invocation of a single unit test is invoked from
<file directory path>/KaggleGenAICapstone2025Q1
python -m unittest <file directory path>/KaggleGenAICapstone2025Q1/agent/test/test_trials.py
