from django.urls import path

from wallet import views

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('greet/<str:name>',views.greeting, name='greet'),
    path('fund/account', views.fund_wallet, name='fund_wallet'),
    path('fund/verify', views.verify_funds, name='verify_fund'),
    path('transfer/funds', views.transfer_funds, name='transfer_funds'),
]