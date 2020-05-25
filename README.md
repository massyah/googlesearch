googlesearch
============

Google search from Python.
Forked from the [Mario Vilas library](https://github.com/MarioVilas/googlesearch). 

Modifications from original library 
=================================== 
* Results are structured and provide description, breadcrumbs, last time updated etc.
* Results are modeled as a dataclass 
* Removed logic to iterate through page results : only the firs page is returned (increase the number of results to get e.g. the top 100 results)
* Works with latest google results page structures (as of 2020-05-25)

See the docs of the original package:

https://python-googlesearch.readthedocs.io/en/latest/

Usage example
-------------

    # Get the first 20 hits for: "Breaking Code" WordPress blog
    from googlesearch import search
    for url in search('"Breaking Code" WordPress blog', stop=20):
        print(url)

Installing
----------

    pip install google
