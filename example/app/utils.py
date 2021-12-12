def orders_filler():
    import random
    import string
    from django.utils import timezone

    from .models import Order, Article, Customer

    now = timezone.now()

    tnt = Article.objects.filter(code='TNT').first()
    willy = Customer.objects.filter(name='Willy').first()

    if not tnt or not willy:
        raise ValueError('article or customer are empty')

    for x in range(1,200):
        o = Order()
        o.id = x
        o.article = tnt
        o.customer = willy
        o.description = 'beep beep will be mine!'
        o.code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        o.created_at = now + timezone.timedelta(days=x)
        o.save()

    pizza = Article.objects.filter(code='PIZZA').first()
    mario = Customer.objects.filter(name='Mario').first()

    if not pizza or not mario:
        raise ValueError('article or customer are empty')
    
    for x in range(200,400):
        o = Order()
        o.id = x
        o.article = pizza
        o.customer = mario
        o.description = 'very hungry bro..please hurry up!'
        o.code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        o.created_at = now + timezone.timedelta(days=x)
        o.save()