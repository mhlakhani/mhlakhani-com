---
title: Classes, Introspection, and the Power of Dynamic Languages
kind: article
created_at: 2011/01/25
tags: [python]
featured: 0
excerpt: This is the third post in the Bulk Tag Generation in Python series.
---

Note: This is the third post in the [Bulk Tag Generation in Python](/blog/2011/01/bulk-tag-generation-in-python/) series.

Last time we went over how to open and read an Excel file. This time we'll actually use that to read in the data file which had all the information we needed to make tags. Here's a sample of the data:

<pre class="prettyprint">Team ID  Delegate ID  Delegate Name   Delegate Email  Delegate Phone  Gender  Age Delegate Level  Accommodation Request   Accommodation Status    Head Delegate  
PSI-S-0001  PSI-D-0001  Hasnain Lakhani some-email-address@gmail.com  123456789  Male 19  University  No   Yes
</pre>

Someone coming from a C++ background might have chosen to start by making a class and having variables such as team id, delegate id, and so on. But that's a lot of boilerplate code to write just to get started.

**I hate boilerplate code**. Quoting [Wikipedia](http://en.wikipedia.org/wiki/Boilerplate_(text\)),

> In computer programming, boilerplate is the term used to describe sections of code that have to be included in many places with little or no alteration. It is more often used when referring to languages which are considered verbose, i.e. the programmer must write a lot of code to do minimal jobs.

Let's see how we can do it in Python.

<pre class="prettyprint"># This is at the top of the file
DELEGATE_FIELDS = "Team ID|Delegate ID|Delegate Name|Delegate Email|Delegate Phone|Gender|Age|Delegate Level|Accommodation Request|Accommodation Status|Head Delegate"

# This is the class we're making
class Thing:

  def __init__(self, sheet, line, fields):

    fields = [x.lower().replace(" ", "_") for x in fields.split("|")]
    for col, field in enumerate(fields):
      self.__dict__[field] = sheet.cell(line, col).value

# And this is how we get all the data
things = [Thing(sheet, x, DELEGATE_FIELDS) for x in xrange(1, maxno)]
</pre>

Let's work through this step by step.

First, we have the <code class="prettyprint">DELEGATE_FIELDS</code> constant, which is basically one long string (copied off the excel file) containing the column names.

Then, we create a class (You can see how good I am at picking names) and define its constructor, the <code class="prettyprint">__init__</code> method. The arguments are simple, sheet is an xlrd worksheet, line is the line number, and fields is the format specifier, which is <code class="prettyprint">DELEGATE_FIELDS</code> here.

Starting off, we turn the fields parameter into a list using a list comprehension; at the same time making the names more code-friendly, e.g. "Team ID" gets converted to <code class="prettyprint">team_id</code>.

Now we enumerate over all the fields. Enumerate is a nice little function, returning both the index and value so we can use them neatly, instead of <code class="prettyprint">for x in xrange(0, len(fields)):</code>. So now we have the column number and the field name.

Line 11 has the real magic: We first fetch the value that we need from the excel file. Then, we're saving it in the <code class="prettyprint">__dict__</code> dictionary, in the field field. So far, so good. But, <code class="prettyprint">__dict__</code> is special. Internally, all a class' variables are stored inside its <code class="prettyprint">__dict__</code>. So when we update that, we're basically adding a new variable into the class, at runtime. Bingo. So, once this code runs with the above data, we can do <code class="prettyprint">my_variable.team_id</code> and it'll give the team ID.

The last line just runs a list comprehension to get all the rows of the Excel file into a list, for later processing.

And that's it. Just 7 lines of Python. Welcome to the power and freedom of dynamic languages.

\- Hasnain
