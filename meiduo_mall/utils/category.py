from goods.models import GoodsChannel


def get_categories():
    '''
    categories={
        'channels.id':{
            'cat1':[{
                'name':channel.category.name,
                'url':channel.url
                },
            ]
            'cat2':[{
                'name':***,
                'subs':[]
                },
            ]
        },
    }
    '''
    categories = {}
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        if channel.group_id not in categories.keys():
            categories[channel.group_id] = {
                'cat1': [],
                'cat2': []
            }
        channel_group = categories[channel.group_id]
        channel_group['cat1'].append({
            'name': channel.category.name,
            'url': channel.url
        })
        cat2s = channel.category.subs.all()
        for cat2 in cat2s:
            channel_group['cat2'].append({
                'name': cat2.name,
                'subs': cat2.subs.all()
            })
    return categories
