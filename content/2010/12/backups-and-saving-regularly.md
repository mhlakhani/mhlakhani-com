{
    "route": "post",
    "title": "Backups and Saving Regularly",
    "date": "2010/12/25",
    "tags": ["ramblings"],
    "excerpt": "The importance of backing up files regularly."
}

You can never understate the importance of backups and saving your work regularly. I really mean it. Whenever you're working on something that takes more than five minutes of work; try to ensure you have a mechanism to prevent your efforts from going down the drain. This isn't only for your programs, it applies to text editing / document processing as well.

> This rant came about thanks to a combination of my sloppy coding and a flaky DSL connection from STC. Long story short, I lost about three hours of work when my program crashed after the Internet connection disconnected.

Let's see how this could have been prevented.

## Mistake #1: No error checking
Your code should **always** handle any possible errors. Enclose stuff in a try/catch block and exit your program gracefully. If you're lazy, just put the try/catch block in your main function, but do have it there. Thanks to [Murphy's Law](http://en.wikipedia.org/wiki/Murphy%27s_law "Murphy's Law"), something **will** go wrong.

## Mistake #2: Not saving work regularly
In my case, the program only wrote output to the file once it had gathered all the needed data. Which is fine when processing takes a few seconds, but not when it takes a few hours. The crash thus resulted in a large waste of time. Every now and then your program should output the data it has to a file. Usually just a call to output\_stream.flush() (or equivalent in your language) should do it. Some language runtimes automatically flush output to disk when a certain amount of data has been saved, however. Python seems to do this. So, when I opened the file, it had about 5000 items of output in it, so all wasn't lost. Only the last 50 or so items hadn't been saved to the disk.

Now, wait a second. Why was I so angry even though most of the output was there in the file? Well, I quickly changed my code to pick up where it left off from, and ran it again. Then these 5000 items were wiped out. How, you might ask? Let's see the next mistake ...

## Mistake #3: Not opening output files in append mode
Unless you have a very good reason not to, always open your output files in append mode (signified by 'a' in python); not in write mode (signified by 'w'). Append mode adds data to the file if it exists, otherwise it creates a new one. Write mode will over-write the file if it exists. So, there went my data. It could have been avoided though, if not for the next mistake.

## Mistake #4: Not making backups
If I had copied the output file and saved it somewhere else, I wouldn't be writing this post. Alas, it serves as a nice reminder to always have backups of your data. They always come in handy, even though most of the time you hopefully won't be needing them.

Let's hope none of us run into such a problem again, or we might see other posts like this.

Stay tuned for the next post, in which I'll write about what the above mentioned program was actually doing in the first place.

\- Hasnain
