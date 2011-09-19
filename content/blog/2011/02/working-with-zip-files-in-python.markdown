---
title: Working with ZIP Files in Python
kind: article
created_at: 2011/02/13
tags: [python]
featured: 0
excerpt: This is the fourth post in the Bulk Tag Generation in Python series.
---

Note: This is the fourth post in the [Bulk Tag Generation in Python](/blog/2011/01/bulk-tag-generation-in-python/) series.

Working with ZIP files in Python is pretty easy. Just import the <Code class="prettyprint">zipfile</code> module, and you're pretty much done.

Here’s some sample code:

<pre class="prettyprint">import zipfile
myzip = zipfile.ZipFile("something.zip")
file_list = myzip.namelist()
file_data = [myzip.read(filename) for filename in file_list]
</pre>

Just import the module, open the zip, get a file list out, and then you have a list containing all the data in each of the files. Pretty nifty, isn't it?

\- Hasnain

PS: Hopefully the time difference between blog posts will go down soon.
