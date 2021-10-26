{
    "route": "post",
    "title": "Reader's Corner: Behind the Scenes",
    "date": "2014/03/07",
    "tags": ["python", "halwa", "facebook"],
    "excerpt": "Details on getting all the posted links out of a Facebook account and on to a blog.",
    "featured": true
}

# Before we begin

This is the long-winded tale of the adventures of one Hasnain Lakhani as he tried to extract all the links he'd ever shared on his facebook wall and tried to move them to a medium more suitable to browsing and searching.

# Getting the data

The first thing to do when creating pages full of links is to, naturally, get those links from somewhere. If someone wants to get all their personal data from Facebook, one would naturally try to [download your information from facebook.](https://www.facebook.com/help/131112897028467)

The data dump looked to be quite promising, as it seemed to contain all the needed posts, [despite what this url said.](https://www.facebook.com/help/www/405183566203254) Those included the ones in which links were shared, however the actual URLs were not present. That turned out to be a dead-end.

The next attempt was to use [Facebook's Graph API](https://developers.facebook.com/docs/graph-api/) which is intended for developers. This API comes with a very handy [Graph API Explorer](https://developers.facebook.com/tools/explorer) tool, which lets one run queries for data right there in the browser. With that tool, getting the data out was surprisingly easy, as it was just a few repeated API calls to:

<pre><code>/$USER_ID/posts?fields=caption,description,message,id,link,name,type,created_time&limit=500</code></pre>

With all that data out and safely saved to a file, the database was almost ready. All that was needed was a small python script to only save posts that had the "link" attribute, and then pretty-print it out to a *links.txt* file.

# Going from JSON to HTML

Getting the data out was the easy part, the hard part was taking all that data and getting it into an easily browsable form. For the uninitiated, [mhlakhani-com is a set of static files](https://github.com/mhlakhani/mhlakhani-com) that is run through [Halwa, a static site generator.](https://github.com/mhlakhani/halwa)

## Updating Halwa

Halwa works by taking *data* from various sources, running it through various *processors*, and then producing *content* based on templates. The data was all ready, the next step was to write a processor and some content.

Writing the [ReadersCorner processor](https://github.com/mhlakhani/halwa/commit/8d067f42eba9eed7e7ea29132089de35251383a3#diff-1d8e973b4c4216ab86477befc562e83dR350) was fairly simple. It first loads a data file and keeps entries that pass a certain filter. Then the entries are sorted into different dictionaries based on their timestamps, and these dictionaries are kept around for later use.

The [ReadersCornerPage content item](https://github.com/mhlakhani/halwa/commit/8d067f42eba9eed7e7ea29132089de35251383a3#diff-1d8e973b4c4216ab86477befc562e83dR168) was also fairly simple to write. It just loops over all the month dictionaries created by the processor and renders the user-defined template for that month.

## Telling Halwa what to do

Now that the content and processor were ready, it was time to actually run them. That was not difficult at all, since it was just a matter of adding some routes and telling Halwa to [run the processor and generate content.](https://github.com/mhlakhani/mhlakhani-com/commit/30d97b721e6ded25795b18d018b554bf548d0038#diff-fdf313ed2303059c44a9ebfffbef8eebR71). Along with adding a template [here](https://github.com/mhlakhani/mhlakhani-com/commit/30d97b721e6ded25795b18d018b554bf548d0038#diff-594ffc48c50179819e12762091ad9f68R1) and [there.](https://github.com/mhlakhani/mhlakhani-com/commit/30d97b721e6ded25795b18d018b554bf548d0038#diff-d5323cae6ea2823a49c71928f3c083bbR1)

## Filtering out personal data

That was all fair and dandy, all the links were up and ready to go online; aside from one *teeny* problem: a privacy leak. The problem, dear reader, was that the facebook posts sometimes contained tags naming friends. Those had to be scrubbed to remove personally identifying information. And, of course, Reader's corner was no place for silly youtube links. [The filter function came to the rescue,](https://github.com/mhlakhani/mhlakhani-com/commit/30d97b721e6ded25795b18d018b554bf548d0038#diff-fdf313ed2303059c44a9ebfffbef8eebR6) removing all URLs that contained a forbidden url/domain component, and replacing any occurrences of names with placeholder names. It's not perfect, since some names within quotes get replaced, but it gets the job done.

# Searching the data

The data was easily browsable in HTML format, however it was still quite tough to search the data to find that one link that was shared a while ago that talked about that thing ...

What was needed was an easy interface to search through all the links. Moreover, it had to be something that worked with static sites, since the rest of the site was static. There could have been a JavaScript solution with a server-side backend that did the searching, but that didn't sound fun. What sounded fun, however, was having all the search done completely client side. 

## Inverted Indexes

An [Inverted Index](http://en.wikipedia.org/wiki/Inverted_index) is one of the standard ways to allow quick full-text searches across a database. At a high level, an inverted index stores each word, and, for each word, a list of documents that contain the given word. Searching is fairly simple, one simply needs to look up the word in the index and then display the appropriate documents (if any).

Generating an inverted index out of the *links.txt* file and transmitting it to the client seemed to be the way to go. The index wasn't too large either, about 210KB before compression for 784 links. 

On a side-note, the [Aho-Corasick string matching algorithm](http://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_string_matching_algorithm) is a data structure which allows fast substring searches. However, the generated index takes about three times the space as compared to an inverted index, so it was deemed infeasible. 

## Updating Halwa yet again

The first thing to do was update the [ReadersCorner Processor](https://github.com/mhlakhani/halwa/commit/3e4f266ea1c148daccb8cc081c1cbc16856e4c06#diff-1d8e973b4c4216ab86477befc562e83dR423) so that it would generate the inverted index. The index generation was fairly straightforward. All the text in each entry was concatenated, then tokenized, stopwords (such as "a", "an") were removed, and then each word was associated with the document ID of the current.

A new *content* type, the [ReadersCornerJSONItem](https://github.com/mhlakhani/halwa/commit/3e4f266ea1c148daccb8cc081c1cbc16856e4c06#diff-1d8e973b4c4216ab86477befc562e83dR210) was also added, which created one JSON file per entry in the database. These files were later used by the UI to display the search results (since the index only contained IDs).

## Writing a basic static search UI

Search isn't all about data: the UI is quite important as well. In fact, it should provide suggestions as the user types. Which sounds just like something an [Autocomplete plugin would have](http://jqueryui.com/autocomplete/). After adding an HTML template and some [javascript code to display the results](https://github.com/mhlakhani/mhlakhani-com/commit/ee7cc3a0744d0ec48cd04c9fa215d0cbad480bdf#diff-c49a0258208bdb0475814bb1a0da0243R24), the search was up and running. The results were fairly primitive, however, and search only worked for keywords.

## Supporting multi-term searches

Once an inverted index is ready, supporting a search query containing multiple terms is fairly straightforward. To get the results of an AND query, one simply just does a set intersection over the results of the document sets for each keyword. For OR, one simply does a set union for those sets. However, the user shouldn't have to type AND or OR between every keyword, so the search UI does two queries; one AND-ing all the keywords, and the other OR-ing all the keywords, and displays the AND results first. This was fairly straightforward to implement, by adding a [complexSearch function.](https://github.com/mhlakhani/mhlakhani-com/commit/8663ceb745e3136c0aa511ab768d967fffdcc00f#diff-c49a0258208bdb0475814bb1a0da0243R38)

Another problem with the search was that searches weren't being done when the enter key was hit, only when a term was selected from the UI. This was easy to fix by [handling the keypress event.](https://github.com/mhlakhani/mhlakhani-com/commit/8663ceb745e3136c0aa511ab768d967fffdcc00f#diff-c49a0258208bdb0475814bb1a0da0243R176)

## Supporting permalinks

The search UI was useful, but it wasn't "social" (insert buzzword of choice). There was no way to share the results of a search query on the database. Thankfully, the HTML5 History API came to the rescue. It allows Javascript code on a page to manipulate the history of a web page. More importantly, it makes it possible for the search UI to automatically update the URL so it can be shared, and then read off that URL so that it can automatically issue a search query when the page is first loaded. All that was needed was a [function to parse the query string and issue a search.](https://github.com/mhlakhani/mhlakhani-com/commit/a6cb2008b958f3bd3dce9968112ae602ac698b99#diff-c49a0258208bdb0475814bb1a0da0243R213)

# Automatically updating Reader's Corner

The solution was all ready to be deployed, except for one *small* problem; the lack of an automatic update. Given the average frequency of posts, poor Hasnain would have to manually update the database multiple times a day, which was clearly not an acceptable solution. Somehow, somewhere, somewhen, ReadersCorner would have to be automatically updated.

## Getting the data, again and again

The first order of data was to automatically get data from Facebook, programmatically, using the API, and then updating the *links.txt* file with new data. This was fairly straightforward:

<pre>
<code class="language-python">
def load():
    with open('links.txt') as input:
        links = json.load(input)
    return links

def get_new_links():
    graph = facebook.GraphAPI(ACCESS_TOKEN)
    query = graph.get_connections("me", "posts", limit=500, fields=','.join(['caption', 'description', 'message', 'id', 'link', 'name', 'type', 'created_time']))
    new_links = query.get('data', [])
    new_links = [l for l in new_links if 'link' in l]
    return new_links

def main():
    links = load()
    new_links = get_new_links()
    ids = set(l['id'] for l in links)
    count = 0

    for link in new_links:
        if link['id'] not in ids:
            links.append(link)
            count = count + 1

    links = sorted(links, key = lambda l: l['created_time'], reverse = True)

    if count > 0:
        with open('links.txt.new', 'w') as output:
            output.write(json.dumps(links, sort_keys=True, indent=4))
        print('%s new links!' % count)
    else:
        print('No new data!')
</code></pre>

What is that magical access token, you may ask?

## Access Tokens

The wizards of Facebook-land do not give up their data to any warm-blooded adventurer. To access their locked box of data, one requires a mythical key, the fabled "access token". Access tokens obtained through the Graph API explorer are short lived, only lasting a few hours. Clearly, a longer access token was needed.

The solution, unfortunately, is to register for a developer account and create a Facebook app. Once that's done, one can get the two ingredients needed to create the mythical access token: an APP_ID and a SECRET.

The basic access token is received by visiting the following url:

<pre><code>https://www.facebook.com/dialog/oauth?type=user_agent&client_id=APP_ID&redirect_uri=REDIRECT_URI&scope=read_stream,export_stream</code></pre>

<code>REDIRECT_URI</code> should be a URL you control, the result will be appended as a query string parameter. This token should be copied and fed into the following URL to get a long lived access token:

<pre><code>https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=SECRET&fb_exchange_token=TOKEN</code></pre>

## Running a static site generator, again and again

With that update program in place, all that's needed is to call it repeatedly, and then call halwa to generate the new website. This is easily done with a shell script:

<pre>
<code class="language-bash">
#!/bin/bash

FILE=/tmp/update_link_log

cd /path/to/folder
. env/bin/activate

rm -f $FILE
python update.py >$FILE 2>&1

if [ $? != 0 ];
then
    echo "Error updating data!"
    exit 1;
fi

if grep --quiet "No new data!" $FILE;
then
    true
else
    now=$(date +"%Y_%m_%d_%H_%M_%S")
    diff links.txt links.txt.new >>$FILE 2>&1
    mv links.txt links.txt.old_$now
    mv links.txt.new links.txt
    python -m halwa config.py | grep -v "json" >>$FILE 2>&1
    cat $FILE
fi
</code></pre>

This script is then run every hour by cron, which emails the output using msmtp to provide a notification whenever there is new data, or whenever an error occurs.

And there, dear reader, is the story of ReadersCorner.

\- Hasnain

PS: At least I got this post out before the 2 year anniversary of the last post.
