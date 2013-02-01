{
    "route": "post",
    "title": "Article Series - Bulk Tag Generation in Python",
    "date": "2011/01/12",
    "tags": ["python"],
    "excerpt": "Series of articles on how to generate image tags in Python."
}

It's time for the first big article series. We'll see how Python (and scripting in general) can really save your time if used correctly. Here's some background information:

PsiFi is a science olympiad, founded and run by students at the [LUMS SSE](http://sse.lums.edu.pk/). You can read more about it [here](http://2011.lumspsifi.org/). When the event rolled around this year, there was a rush to generate tags for the 800 or so delegates attending the event; in addition to about 200 tags for the host team. Last year, they all had to be made by hand in Photoshop (poor Safdar). That's inefficient, both in terms of driving people nuts, and in terms of mistakes (he got my picture upside down on the tag!). This year, the responsibility fell on me. I couldn't be bothered making all the tags by hand, and I had no idea how to use Photoshop.

Enter Python and it's rich variety of libraries to the rescue. With just a few hours' work, all the tags were generated and ready for printing. When the template design changed, it only took a few clicks and a few minutes of processing time to generate all the tags again. Safdar would have been murderous if he was asked to make all those tags again.

In this article series, there will be a bunch of self contained  posts describing how to do the various sub tasks, and then a post or two describing how they come together.

Topics list:

1. [Decorators and timing your code](/blog/2011/01/decorators-and-timing-your-code/)
1. [Reading Excel files in Python](/blog/2011/01/reading-excel-files-in-python/)
1. [Classes, Introspection, and the power of Dynamic Languages](/blog/2011/01/classes-introspection-dynamic-languages/)
1. [Working with ZIP files in Python](/blog/2011/02/working-with-zip-files-in-python/)
1. Memory mapped files in Python: The StringIO Module
1. Image Processing in Python with the PIL Module (This might be broken into two parts)
1. Bringing it all together part 1: The Delegate Tags
1. Duck typing: If it walks like a duck and talks like a duck, it probably is one
1. Working with global variables in Python
1. Bringing it all together part 2: The Volunteer Tags

Whew. That's certainly a lot. It should definitely keep me busy for the next month or so at least.

Stay tuned!

\- Hasnain
