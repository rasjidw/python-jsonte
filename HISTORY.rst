.. :changelog:

History
-------

0.8.5 (2015-08-09)
------------------
* Bugfix: fix an issue when _one_shot was used in iterencode in non-2.6 versions of Python

0.8.4 (2015-08-06)
------------------
* Major reworking
    - Make jsonte a module rather than a package, since the scope is small enough to do so.
    - Remove top level functions and put the core functionality into a class that is instantiated.
    - Allow a custom objecthook to be used.
    - Allow the ability to enforce json 'websafety' through raising an exception or prefixing the string.
    - Allow additional type serialisers to be added in any order (subclasses no longer need to go first).
    - Support for Python 2.6, 3.3 and 3.4 (as initially just 2.7)


0.8.3 (2015-06-08)
------------------
* Base SerialisationDict on a separate a mixim class to provide more flexability.


0.8.2 (2015-06-04)
------------------
* Rename JsonteDict to SerialisationDict to add clarity.
* Give access to the registered type classes.


0.8.0 (2015-05-22)
------------------
* Initial version
