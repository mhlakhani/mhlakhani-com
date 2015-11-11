import sys
import re
from functools import partial
from collections import OrderedDict

def namefilter(forbidden_urls, forbidden_domains, names, extra_names, whitelist, nameset_ignores, placeholders, entry):

    link = entry.get('link')
    if link is None:
        return None

    if entry['type'] == 'photo' or entry['type'] == 'status':
        return None

    names = names + extra_names
    nameset = set(s for s in ' '.join(names).split(' ') if len(s) > 2) - nameset_ignores

    for url in forbidden_urls:
        if link.find(url) != -1:
            return None

    if 'caption' in entry:
        for domain in forbidden_domains:
            if entry['caption'].find(domain) != -1:
                return None

    holder = 0

    message = entry.get('message', '')
    if message is not None:
        for name in names:
            if message.find(name) != -1:
                #print('Removing name %s' % name)
                message = message.replace(name, placeholders[holder])
                holder = holder + 1
        for name in nameset:
            if message.find(name) != -1:
                fp = False
                for placeholder in placeholders:
                    if message.find(placeholder) != -1 and placeholder.find(name) != -1:
                        fp = True
                st = re.findall("[\w']+|[.,!?;]", message)
                if name not in st:
                    fp = True
                if not fp and entry['id'] not in whitelist:
                    message = message.replace(name, placeholders[holder])
                    holder = holder + 1
                    #print('Removing name substring match %s in %s' % (name, entry['id']))
        entry['message'] = message

    return entry

try:
    sys.path.insert(0, '.')
    import filterdata
    _filter = partial(namefilter, filterdata.forbidden_urls, filterdata.forbidden_domains, filterdata.names, filterdata.extra_names, filterdata.whitelist, filterdata.nameset_ignores, filterdata.placeholders)
except Exception:
    print('WARNING: Could not import filter data, ReadersCorner may contain personal info! ABORTING!')
    import traceback
    traceback.print_exc()
    sys.exit(1)

routes = {
        'index' : '/',
        'publications' : '/publications/',
        'blogindex' : '/blog/',
        'blogarchives' : '/blog/archives/',
        'blogrss' : '/blog/rss.xml',
        'sitemap' : '/sitemap.xml',
        'post' : '/blog/{year}/{month}/{slug}/',
        'tag' : '/blog/tag/{tag}/',
        'resume' : '/static/pdf/resume.pdf',
        'readerscornerhome' : '/readers-corner/',
        'readerscornerpage' : '/readers-corner/{year}/{month}/',
        'readerscornersearch' : '/readers-corner/search/',
        'readerscornerjsonitem' : '/readers-corner/search/{id}.json'
}

base_deps = ['templates/base.haml', 'templates/macros.haml']
post_deps = ['templates/base.haml', 'templates/macros.haml', 'templates/blogpost.haml', 'tags']
readers_corner_deps = base_deps + ['readerscorner', 'readerscornersidebar', 'readerscornerindex']

sources = [
        ('Page', 'content/index.haml', {}, base_deps),
        ('Page', 'content/publications.haml', {}, base_deps),
        ('Page', 'content/blog*.haml', {'blogsidebar' : 'sidebar'}, post_deps),
        ('BlogPost', 'content/*/*/*.md', {'blogsidebar' : 'sidebar', 'blogposttemplate' : 'template', 'blogpostonload' : 'onload'}, post_deps),
        ('TagPage', 'content/tag.haml', {'blogsidebar' : 'sidebar'}, post_deps),
        ('Page', 'content/rss.xml', {}, ['rss']),
        ('Page', 'content/sitemap.xml', {}, ['sitemap']),
        ('StaticContent', 'static/css/*.css', {}, []),
        ('StaticContent', 'static/js/*.js', {}, []),
        ('StaticContent', 'static/pdf/*.pdf', {}, []),
        ('StaticContent', 'static/img/*/*/*', {}, []),
        ('Page', 'content/readerscornerhome.haml', {'readerscornersidebar' : 'sidebar'}, readers_corner_deps),
        ('ReadersCornerPage', 'content/readerscornerpage.haml', {'readerscornersidebar' : 'sidebar', 'readerscorner' : 'readerscorner'}, readers_corner_deps),
        ('Page', 'content/readerscornersearch.haml', {'readerscornersidebar' : 'sidebar', 'readerscornerindex' : 'readerscornerindex'}, readers_corner_deps),
        ('ReadersCornerJSONItem', 'content/readerscornerjsonitem.json', {'readerscornersidebar' : 'sidebar', 'readerscorner' : 'readerscorner'}, readers_corner_deps),
]

processors = [
    ('TagList', {'key' : 'tags', 'datakey': 'tags', 'sortkey': 'date', 'route': 'tag'}),
    ('BlogSidebar', {'key' : 'blogsidebar', 'routes' : 'blogsidebarroutes', 'tags' : 'tags', 'routekey' : 'links'}),
    ('PostList', {'key' : 'featuredposts', 'count': 5, 'sortkey' : 'date', 'uniquekey': 'slug', 'reverse' : True,
        'filters' : [lambda p: p.get('featured', False)], 'exclude' : ''}),
    ('PostList', {'key' : 'recentposts', 'count' : 5, 'sortkey' : 'date', 'uniquekey': 'slug',
        'filters' : [], 'reverse' : True, 'exclude' : 'featuredposts'}),
    ('PostArchives', {'key' : 'blogarchives'}),
    ('RSSFeed', {'key' : 'rss', 'count' : 5, 'title' : "Hasnain Lakhani's Blog", 'link': 'http://mhlakhani.com/blog/', 'description': "Hasnain Lakhani's Blog", 'sortkey': 'date'}),
    ('Sitemap', {'key' : 'sitemap', 'root' : 'http://mhlakhani.com'}),
    ('ReadersCorner', {'key' : 'readerscorner', 'filename' : 'links.txt', 'sidebarkey' : 'readerscornersidebar', 'indexkey' : 'readerscornerindex', 'route' : 'readerscornerpage', 'filter' : _filter, 'homeroute' : 'readerscornerhome', 'searchroute' : 'readerscornersearch', 'stopwords' : filterdata.stopwords})
]

data = {
    'blogsidebarroutes' : OrderedDict(pair for pair in [
        ('Blog Home', 'blogindex'),
        ('Archives','blogarchives'),
        ('RSS Feed','blogrss')
    ]),

    'blogposttemplate' : 'blogpost.haml',
    'blogpostonload' : 'prettyPrint();'
}

directories = { 'templates' : 'templates', 'output' : 'output' }
