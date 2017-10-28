|PyPI| |PyPI2| |Documentation Status|

About
=====

A Python module for connecting to the Adobe Echosign REST API, without
the hassle of dealing with the JSON formatting for requests/responses
and the REST endpoints and their varying requirements

Documentation
-------------

The most up to date documentation can be found on `pyEchosign’s RTD
page`_.

Maintained on GitLab
--------------------

This project is maintained on `GitLab`_ and mirrored to `GitHub`_.
Issues opened on the latter are still addressed.

Notes
=====

JSON Deserialization
--------------------

Most classes contain two methods to facilitate the process of receiving
JSON from the REST API and turning that into Python classes. One,
``json_to_X()`` will handle the JSON formatting for a single instance,
while the second - ``json_to_Xs()`` processes JSON for multiple
instances. Generally, the latter is simply returning a list
comprehension that calls the former.

While this is primarily useful for internal purposes - every method
retrieving an ``Agreement`` from the API will call
``Agreement.json_to_agreement()`` for example - the methods are not
private and available for use. Any changes to their interface will only
be made following deprecation warnings.

Internal Methods and Classes
----------------------------

All protected and private methods; and any classes, functions, or
methods found under ``pyEchosign.utils`` are subject to change without
deprecation warnings however.

.. _pyEchosign’s RTD page: http://pyEchosign.readthedocs.io/en/latest/
.. _GitLab: https://gitlab.com/jensastrup/pyEchosign
.. _GitHub: https://github.com/JensAstrup/pyEchosign

.. |PyPI| image:: https://img.shields.io/pypi/v/pyEchosign.svg
   :target: https://pypi.python.org/pypi/pyEchosign
.. |PyPI2| image:: https://img.shields.io/pypi/pyversions/pyEchosign.svg
   :target: https://pypi.python.org/pypi/pyEchosign
.. |Documentation Status| image:: https://readthedocs.org/projects/pyechosign/badge/?version=stable
   :target: http://pyechosign.readthedocs.io/en/stable/?badge=stable