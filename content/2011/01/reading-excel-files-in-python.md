{
    "route": "post",
    "title": "Reading Excel Files in Python",
    "date": "2011/01/18",
    "tags": ["python", "excel"],
    "excerpt": "This is the second post in the Bulk Tag Generation in Python series."
}

Note: This is the second post in the [Bulk Tag Generation in Python](/blog/2011/01/bulk-tag-generation-in-python/) series.

If you've ever had a small data set to work with; or had a data set provided by a non-technical user, it would probably have been an Excel file. Now, working with that in Excel itself sometimes becomes a pain, so we can get around that limitation by using the [xlrd](http://www.python-excel.org/) module.

With this module, working with Excel 2003 files is a breeze (it doesn't have support for 2007 yet, unfortunately). Let's just jump into the (mostly self explanatory) code:

<pre class="prettyprint">import xlrd
wkbk = xlrd.open_workbook('data.xls')
sheet = wkbk.sheet_by_name('Sheet 1')
data = sheet.cell(row_number, column_number).value
</pre>

And that's all you need to do. Simple and useful. The module handles type conversions automatically, so if your cell is formatted as a 'number', it will automatically be a float, not a string. Just note that row and column numbers are zero based, so the first row is row 0.

Next time, we'll cover how to read in a small-sized data set and keep it manageable in Python, using its dynamic nature.

\- Hasnain
