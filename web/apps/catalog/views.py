from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from apps.catalog.models import Category, Product

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.select_related('category').filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'catalog/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    return render(request, 'catalog/product/detail.html', {
        'product': product,
        'related_products': related_products
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog:product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
