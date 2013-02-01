{
    "route": "post",
    "title": "Decorators and Timing your code",
    "date": "2011/01/15",
    "tags": ["python"],
    "excerpt": "This is the first post in the Bulk Tag Generation in Python series."
}

Note: This is the first post in the [Bulk Tag Generation in Python](/blog/2011/01/bulk-tag-generation-in-python/) series. This post is fairly technical and covers some important programming concepts, but it's not vital if you just want to get to generating some tags.

When you're hacking together some code, it often helps to get a rough idea of how fast various functions are. Wouldn't it be great to do this in a simple and easy way? With function decorators, doing this is insanely easy. Imagine for a second that you have a "print_timing" decorator from somewhere. Now, all you need to do to time your function is:

<pre class="prettyprint">@print_timing
def foo(a,b,c):
    # all your codes are belong here
</pre>

The decorator will take care of the rest. The @print_timing line is basically syntactic sugar for applying the decorator to the function. Let's break it down and see how to write this code.

### Step 1: The Timing

When timing a function, the simplest you can do is just measure how long it took in wall clock time (this isn't exactly the time taken to evaluate the function, but we'll use it for simplicity). The code here isn't too complicated:

<pre class="prettyprint">def wrapper():
    t1 = time.time()
    res = func()
    t2 = time.time()
    print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
    return res
</pre>

Our wrapper function just calls the func function and prints how long it took. It returns the result of the function. This is important, otherwise the result of the function is lost, and we usually want the result! Note: functions are first class objects in Python, you can just do stuff like func.func\_name to get the name of the function in the func variable.

So, now you can just call the wrapper() function instead of calling the func() function and you'll be done. But this approach has a few problems.

* It's sort of hard coded. The function to call is hard coded in line 3. So you'll need a different wrapper function for each function you want to time.
* You have to search and replace all your calls to func() to calls to wrapper(), which is inefficient and a pain to reverse when you want to stop measuring the time.
* This can only handle functions with no arguments. You'll need to modify it for each function you use, changing the argument list appropriately.

What a pain!

### Step 2: Handling input arguments

Time for some python magic. Replace lines 1 and 3 above with the following:

<pre class="prettyprint">def wrapper(*args, **kwargs):

    res = func(*args, **kwargs)
</pre>

Okay.. what the heck is that supposed to mean? As you can read [here](http://www.saltycrane.com/blog/2008/01/how-to-use-args-and-kwargs-in-python/), Python allows one to use a variable number of arguments for a function (and also keyword arguments). This way, our wrapper function can accept any number of arguments, for example <code class="prettyprint">wrapper(1,2,'hello',dir=3,folder=2)</code> would call wrapper with args as a list: <code class="prettyprint">[ 1,2,'hello' ]</code> and kwargs as a dictionary: <code class="prettyprint">{'dir':3, 'folder':2}</code>. This way the function can process any number of arguments. But here, all we want to do is pass these arguments on to func, so it can do its work. That's done using the syntax in line 3. Now it's slightly better, we just have to copy paste this function, instead of changing the arguments each time.

But that still sucks.

### Step 3: Time for some decoratin'
Now for a little detour into functional programming (FP). One of the great concepts in FP is that of [higher order functions](http://en.wikipedia.org/wiki/Higher-order_function), i.e. functions that operate on other functions. This may be a little odd if you're coming from the world of C/C++, but it's an extremely useful concept.

A decorator is just a higher order function. It takes your original function (let's call it foo), and returns another function (let's call this one bar) that does something else. When you apply this using the @ syntax, bar gets called instead of foo. A decorator gets passed in a single argument, which is the function it is decorating. So, let's write a simple function that takes a function, and returns it buried inside our wrapper function:

<pre class="prettyprint">def print_timing(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        t2 = time.time()
        print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
        return res
    return wrapper
</pre>

Whoa. Here's another great thing, we can nest functions inside functions. Since the wrapper function is now inside print_timing, it can access the func variable. So it can call any function, as functions are just variables and can be passed around as such (hello, FP. goodbye, C++). And it returns this function, so Python knows to call our wrapped function instead of the original function.

Aaand we're done. Now, as you saw in the snippet above, all you need to do is write @print\_timing before the function you want to time, and delete that line when you want to stop timing it. Gotta love the magic!

If you want to read up more on decorators, check out the second answer [here](http://stackoverflow.com/questions/739654/understanding-python-decorators). It should clear up a ton of things.

On a last note, please don't use this function for any real benchmarks. It's just to get a rough idea, and it's not scientific or highly accurate. Look into the timeit module for details.

\- Hasnain
