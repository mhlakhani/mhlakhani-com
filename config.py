from collections import OrderedDict

routes = {
        'index' : '/',
        'blogindex' : '/blog/',
        'blogarchives' : '/blog/archives/',
        'blogrss' : '/blog/rss.xml',
        'sitemap' : '/sitemap.xml',
        'post' : '/blog/{year}/{month}/{slug}/',
        'tag' : '/blog/tag/{tag}/',
        'resume' : '/resume/'
}

base_deps = ['templates/base.haml', 'templates/macros.haml']
post_deps = ['templates/base.haml', 'templates/macros.haml', 'templates/blogpost.haml', 'tags']

sources = [
        ('Page', 'content/index.haml', {}, base_deps),
        ('Page', 'content/resume.haml', {}, base_deps),
        ('Page', 'content/blog*.haml', {'blogsidebar' : 'sidebar'}, post_deps),
        ('BlogPost', 'content/*/*/*.md', {'blogsidebar' : 'sidebar', 'blogposttemplate' : 'template', 'blogpostonload' : 'onload'}, post_deps),
        ('TagPage', 'content/tag.haml', {'blogsidebar' : 'sidebar'}, post_deps),
        ('Page', 'content/rss.xml', {}, ['rss']),
        ('Page', 'content/sitemap.xml', {}, ['sitemap']),
        ('StaticContent', 'static/css/*.css', {}, []),
        ('StaticContent', 'static/js/*.js', {}, []),
        ('StaticContent', 'static/pdf/*.pdf', {}, []),
        ('StaticContent', 'static/img/*/*/*', {}, []),
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
    ('Sitemap', {'key' : 'sitemap', 'root' : 'http://mhlakhani.com'})
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
