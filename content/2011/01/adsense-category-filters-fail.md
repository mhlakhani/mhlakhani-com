{
    "route": "post",
    "title": "AdSense Category Filters Fail",
    "date": "2011/01/30",
    "tags": ["adsense", "ramblings"],
    "excerpt": "AdSense Category filters are pretty useless. Let's see why.",
    "featured": true
}

(Warning: long rant ahead)

Some of you may have noticed the ads now showing on the sidebar (or not, if you're using AdBlock, which I highly recommend). Having heard a lot about Google AdSense and the money people rake in from ads, I wanted to give it a spin and try it out. Given that this is a personal blog and ads look cheap, they may not last long.

**Especially when a personal, tech blog gets ads such as "Sexy Girls in KSA".**

That was one of the first ads shown on my blog, right after setting them up (unfortunately there's no screen shot, that really wasn't the first thing on my mind then). The code was quickly removed while I looked for a solution. That's when I stumbled upon the [Category Filtering](http://www.google.com/adsense/support/bin/answer.py?hl=en&answer=9346) option. In short, it lets you filter ads by category. To list one from that page:

> Dating: Includes dating services and online dating communities.

Sounds perfect! I quickly searched for documentation, finding some good screenshots at this [site](http://www.ditii.com/2010/10/04/adsense-general-category-blocking-beta-test-begins/).

{{ macros::image(src='/static/img/2011/01/adsensefail1.jpg', caption='Category Filtering Options') }}

So, I login to my own adsense account, and here's what I see:

{{ macros::image(src='/static/img/2011/01/adsensefail2.jpg', caption='Options are Hidden') }}

The option simply isn't available. Tough luck. It seems like there's no chance at all for folks like me. Some more digging around lead me to the following post, from the [Google Adsense Blog](http://adsense.blogspot.com/2011/01/sensitive-category-blocking-now.html):

> "This week, publishers in Thai, Turkish, and Russian-speaking countries can now block ads in sensitive categories for all supported languages. "

The interesting (and depressing!) part is that category filtering depends on the publisher's country. From a technical point of view, I can't think of any reason ad filtering should depend on the language of the publisher's country. Sure, if it depended on the Ad and/or site language, it would have made sense. But this? Really?

Someone from Pakistan can't filter ads on his site, just because his country's official language is not English. Never mind that the ads are in English, just like the rest of the site's content.

I guess I'll have to wait for someone more knowledgeable to explain this.

[/rant]

\- Hasnain
