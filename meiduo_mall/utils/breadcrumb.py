def get_breadcrumb(cat3):
    cat2 = cat3.parent
    cat1 = cat2.parent
    breadcrumb = {
        'cat1': {
            'name': cat1.name,
            'url': cat1.goodschannel_set.all()[0].url
        },
        'cat2': cat2,
        'cat3': cat3
    }
    return breadcrumb