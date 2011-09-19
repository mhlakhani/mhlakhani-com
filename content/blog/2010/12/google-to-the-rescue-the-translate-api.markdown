---
title: Google to the Rescue - The Translate API
kind: article
created_at: 2010/12/27
tags: [python]
featured: 0
excerpt: Using the google Translate API from Python.
---

As promised in the last [post](/blog/2010/12/backups-and-saving-regularly/), here's the piece of code that had horrible bugs in it. The task was fairly simple: given a small word list in english, I needed to translate it to a few other languages. Now, there's no obvious way to do it, except for translating the words one by one. Here's where some scripting and google's APIs come in handy. By just fetching a simple URL; the [Translate API](https://code.google.com/apis/language/translate/overview.html) returns its translation in a simple and easy to parse format, [JSON](http://www.json.org/). Note: If you want to go over the limits for anonymous users (which is around 150 words/hour), you'll need an API key, which you can get [here](http://code.google.com/apis/console).

Let's just jump straight into an overview of the code.

<pre class="prettyprint">    import urllib2
    KEY = 'ENTER_YOUR_API_KEY_HERE'
    TARGET = 'ar'

    def fetch_word(word):
        # Process a single word here

    def fetch_all_words():
        # Process the whole word list here
    
    if __name__ == "__main__":
        fetch_all_words()
</pre>

The above is fairly simple, we're just importing the required modules, and defining some variables. The *urllib2* module contains functions to open web URLs (webpages), so we need that.  

Let's jump ahead to the definition of the fetch\_word function:

<pre class="prettyprint">    def fetch_word(word):
        url = 'https://www.googleapis.com/language/translate/v2?key=%s&source=en&target=%s&q=%s' % (KEY, TARGET, word)
        dat = urllib2.urlopen(url).read()
        data = eval(dat)
        trans = data['data']['translations'][0]['translatedText']
        return trans
</pre>

Let's break this down into bite-size parts. First, we generate the URL, which is of the form 

<blockquote>
    https://www.googleapis.com/language/translate/v2?key=ENTER_API_KEY_HERE&source=SOURCE_LANGUAGE&target=TARGET_LANGUAGE&q=WORD_TO_TRANSLATE 
</blockquote>
Once that's done, in line 3, we read all the information at that URL. First we call the *urllib2.urlopen* function, which lets us treat the webpage as a file, and then we call read on it to read everything.

Line 4 is where the magic's at. Google's response is of this form (which is actually JSON, as we noted above.):

<pre class="prettyprint">{"data":
  {"translations":
    [
      {"translatedText":"Bonjour"}
    ]
  }
}
</pre>

This might look a bit strange at first sight, but if you know even a bit of Python, it's just like code to make dictionaries and lists. In fact, using the *eval* function in line 4, we run this as full blown Python code and save the result in the data variable. This is where dynamic languages come in handy, this would be very difficult to do in C/C++! Once we have the data, we simply read our word off it and return it, as in lines 5-6. And that's it. You've just gotten your translated word off google!

Now, in the *fetch\_all\_words* function, all we do is fetch each word in our file, and save the translations to another file:

<pre class="prettyprint">    def fetch_all_words():
        count = 0

        word_list = open('words.txt').read().split('\n')
        out = open("translation.txt", 'a')

        for word in word_list:

            print >> out, '%s = %s' % (word, fetch_word(word))
    
            count = count + 1
            if count % 20 == 0:
                print count
                out.flush()

        out.close()
</pre>

First, we setup a counter variable. In line 4, we open the words.txt file and split it (as it had one word per line) into a list of words, for easier processing. Then we open the output file, **in append mode**.

Then, simply looping over each word in the input list, we fetch its translation, and print output to the output file, with one word and it's translation per line.

Then we have some book-keeping. We increment the counter; and after every 20 words we flush our output to file and print the counter, to get an idea of how much work has been done.

After that, we just close the file as we're done with the loop and all the processing. That's it, now you have a handly little script to translate your word list.

\- Hasnain
