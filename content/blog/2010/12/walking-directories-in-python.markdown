---
title: Walking Directories in Python
kind: article
created_at: 2010/12/23
tags: [python]
featured: 0
excerpt: Tutorial on how to use Python to walk a directory tree.
---
Now for the first **real** post. Here I'll write about how you can use Python scripting to make your life much easier. After all, computers are here to make our lives easier, it's not the other way around.

There was once a directory tree, which had many directories in it; those directories had directories in them, and so on, until infinity. Okay, maybe not. The directory we have stop somewhere, ending up just containing plain old image files.

Another application needed to know what files were present in our mythical directory tree. So we needed to make a directory index listing what subdirectories or files were contained in each directory. Sounds simple enough, maybe we could do it by hand. But wait! There are 5 directories, each having 10 or so sub-directories, each of those having 10 or so images. Here comes Python to the rescue!

Let's get down to the code part. First off, we just write some boilerplate code:

<pre class="prettyprint linenums">    import sys, os, glob

    def make_index(directory):

        # Stuff here

    if __name__ == "__main__":
        make_index('Image')
</pre>

The code is fairly simple:

* Line 1: We import the modules needed
* Line 3: Defining a make\_index function that'll do the real work
* Lines 7&8: Call the make\_index function on the Image directory if we're running the script

The first thing we need to do is check whether the directory we're currently dealing with contains other directories or just contains images. The easiest way to do that is to make a list of all images in this directory and check whether that's empty or not; so let's try that out.

<pre class="prettyprint">    image_list = []

    for ext in ('jpg', 'jpeg', 'bmp', 'png', 'gif'):
        search_str = os.path.join(directory,'*.%s' % ext)
        image_list.extend(glob.glob(search_str))
    
    out = open(os.path.join(directory, 'index.txt'), 'w')
</pre>
        
Like all Python code, this is mostly self explanatory. We try all known image extensions, and construct strings of the form “\*.jpg” 
Then we construct a full path, something like “/Image/\*.jpg”. The glob module does all the heavy lifting, returning a list of all the files that match this string. We then extend our image list to contain all the returned search results. So, when this loop has executed, we've got a list of all images in the current directory. Viola. Once that's done, we just create an “index.txt” file in the current directory, where we'll write our results.

Now to fill the index file with appropriate stuff. First we check whether the current directory has other directories, or just contains images. Let's build the index for the first case:

<pre class="prettyprint linenums">    if len(image_list) == 0:
        folder_list = [os.path.join(directory, f)
                        for f in os.listdir(directory)
                        if os.path.isdir(os.path.join(directory, f))]
        print >> out, "FOLDER"
        print >> out, "ITEMS|%s" % len(folder_list)
        for f in folder_list:
            make_index(f)
            print >> out, '%s|/%s' % (f.split(os.sep)[-1], 
                os.path.join(f, 'index.txt').replace(os.sep, '/') )
</pre>

That's definitely a mouthful. Lines 2,3, and 4 constitute what's called a List Comprehension in Python. After this code runs, folder\_list contains the full directory names of all subdirectories inside the current directory. os.path.join builds the full directory name, os.listdir lists all the subdirectories, and os.path.isdir lets us know if something is a directory or not.

Next, we print some basic information out into the file, with line 5 printing “FOLDER” and line 6 printing “ITEMS|x”, making it easy for someone else to parse the resulting file.

After that, in the for loop, we first make an index for the sub directory, and then print a line listing that sub-directory. Here's where Python shines. First we split the folder name, getting the last element (note that the list index is -1). So, if the path was /a/b/c, this would return 'c'. And then we format the directory name, making it into a full path pointing to the index file. We end up with nice looking strings like: “c|/a/b/c/index.txt”, which are easy to read later on.

Now let's move on to making the index file for images. This is much more straighforward:

<pre class="prettyprint">    else:
        print >> out, "IMAGES"
        print >> out, "ITEMS|%s" % len(image_list)
        for im in image_list:
            print >> out, '/%s' % im.replace(os.sep, '/')
</pre>

We just print out the markers, just like before, and then for each image we just print the full path to the image. And we're done (almost).

The last line we need is the following, which just closes the output file:

<pre class="prettyprint">    out.close()
</pre>

And that's finally it. Now we have a nice little program that makes directory indexes. It definitely saved my time, I'd rather not make those files by hand! To help you get an idea of what it was all about, the sample output's below.

Directory with subdirectories:

<pre class="prettyprint">    FOLDER
    ITEMS|5
    Ahzab|/Image/Ahzab/index.txt
    Badr|/Image/Badr/index.txt
    Mosques|/Image/Mosques/index.txt
    Prophets Gallery|/Image/Prophets Gallery/index.txt
    Uhad|/Image/Uhad/index.txt
</pre>

Directory with images:

<pre class="prettyprint">    IMAGES
    ITEMS|5
    /Image/Badr/badr1.jpg
    /Image/Badr/badr2.jpg
    /Image/Badr/badr3.jpg
    /Image/Badr/badr4.jpg
    /Image/Badr/badr2.bmp
</pre>

Stay tuned for more time saving scripts.

\- Hasnain
