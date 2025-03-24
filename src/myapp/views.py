from django.views.static import serve
from django.conf import settings
from .models import Downloads, Gates
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.offline as pyo
from django.db.models.functions import TruncDay
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from myapp.apps import all_games
import requests
import datetime


IP_ADDRESS = 'HTTP_X_REAL_IP'
USER_AGENT = 'HTTP_USER_AGENT'

def get_ip_address(request):
    return request.META.get(IP_ADDRESS, request.META.get('REMOTE_ADDR', ''))

def get_user_agent(request):
    return request.META.get(USER_AGENT, '')


def check_if_game(link):
    # Определить тип ссылки
    if_game = None
    if 'exports' in link and 'zip' not in link:
        if_game = None
    elif link in all_games:
        if_game = True
    else:
        if_game = False
    return if_game


def games_group_by_regionName(start_date, end_date,if_game=True):
    data = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).values('regionName').annotate(count=Count('id'))
    x_values = [d['regionName'] for d in data]
    y_values = [d['count'] for d in data]
    trace = go.Bar(
        x=x_values,
        y=y_values,
        marker=dict(
            color='rgb(158,202,225)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        ),
        opacity=0.6,
    )
    layout = go.Layout(
        title='Количество скачиваний игр по регионам',
        xaxis=dict(title='Регионы'),
        yaxis=dict(title='Количество скачиваний'),
        width=1000,
        height=600,
    )
    fig = go.Figure(data=[trace], layout=layout)
    plot_div = pyo.plot(fig, auto_open=False, output_type='div')
    return plot_div


def games_group_by_city(start_date, end_date,if_game=True):
    data = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).values('city').annotate(count=Count('id'))
    x_values = [d['city'] for d in data]
    y_values = [d['count'] for d in data]
    trace = go.Bar(
        x=x_values,
        y=y_values,
        marker=dict(
            color='rgb(158,202,225)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        ),
        opacity=0.6,
    )
    layout = go.Layout(
        title='Количество скачиваний игр по городам',
        xaxis=dict(title='Города'),
        yaxis=dict(title='Количество скачиваний'),
        width=1000,
        height=600,
    )
    fig = go.Figure(data=[trace], layout=layout)
    plot_div = pyo.plot(fig, auto_open=False, output_type='div')
    return plot_div


def games_group_by_country(start_date, end_date,if_game=True):
    data = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).values('country').annotate(count=Count('id'))
    x_values = [d['country'] for d in data]
    y_values = [d['count'] for d in data]
    trace = go.Bar(
        x=x_values,
        y=y_values,
        marker=dict(
            color='rgb(158,202,225)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        ),
        opacity=0.6,
    )
    layout = go.Layout(
        title='Количество скачиваний игр по странам',
        xaxis=dict(title='Страны'),
        yaxis=dict(title='Количество скачиваний'),
        width=1000,
        height=600,
    )
    fig = go.Figure(data=[trace], layout=layout)
    plot_div = pyo.plot(fig, auto_open=False, output_type='div')
    return plot_div


def circle_plot_by_games(start_date, end_date,if_game = True):
    # Получаем данные по скачиваниям каждой игры
    downloads_by_game = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).values('gate_app').annotate(count=Count('id')).order_by(
        '-count')

    # Создаем список меток и соответствующих значений для построения круговой диаграммы
    labels = [game['gate_app'] for game in downloads_by_game]
    values = [game['count'] for game in downloads_by_game]

    # Создаем объект диаграммы и добавляем данные
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Настраиваем макет диаграммы
    fig.update_layout(
        title='Круговая диаграмма скачиваний игр',
        margin=dict(l=50, r=50, t=50, b=50),
    )

    # Генерируем HTML-код для диаграммы
    plot_pie = plot(fig, output_type='div')
    return plot_pie


def plot_time_all_game(start_date, end_date,if_game = True):
    # 1 график
    # Создать временной ряд для каждого `gate_app`
    gate_apps = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date)).values_list('gate_app', flat=True).distinct()
    data = []
    for app in gate_apps:
        # Получить даты, за которые были произведены скачивания данного `gate_app`
        dates = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).annotate(date_day=TruncDate('date')).dates(
            'date_day', 'day')

        # Создать временной ряд для данного `gate_app`
        x_values = [d for d in dates]
        y_values = [
            Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).annotate(date_day=TruncDate('date')).filter(
                date_day=date).count()
            for date in dates
        ]

    # Получить даты, за которые были произведены скачивания игр
    game_dates = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).annotate(date_day=TruncDate('date')).dates('date_day', 'day')

    # Создать временной ряд для общего количества скачиваний игр
    game_x_values = [d for d in game_dates]
    game_y_values = [
        Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).annotate(date_day=TruncDate('date')).filter(date_day=date).count()
        for date in game_dates
    ]

    # Добавить временной ряд на график
    game_trace = go.Scatter(
        x=game_x_values,
        y=game_y_values,
        name='Все игры',
        line=dict(color='orange'),
        mode='lines+markers',
    )
    data.append(game_trace)

    # Создать макет для графика
    layout = go.Layout(
        title='Скачивания по приложениям',
        xaxis=dict(
            title='Дата',
            tickformat='%Y-%m-%d',
            hoverformat='%Y-%m-%d'
        ),
        yaxis=dict(
            title='Количество скачиваний'
        )
    )

    # Создать график
    fig = go.Figure(data=data, layout=layout)
    plot_all_games_time = pyo.plot(fig, auto_open=False, output_type='div')
    return plot_all_games_time


def plot_time_each_game(start_date, end_date,if_game = True):
    # 2 график
    # Создать временной ряд для каждого `gate_app`
    gate_apps = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date)).values_list('gate_app', flat=True).distinct()
    data = []
    for app in gate_apps:
        # Получить даты, за которые были произведены скачивания данного `gate_app`
        dates = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game,gate_app=app).annotate(date_day=TruncDate('date')).dates(
            'date_day', 'day')

        # Создать временной ряд для данного `gate_app`
        x_values = [d for d in dates]
        y_values = [
            Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game,gate_app=app).annotate(date_day=TruncDate('date')).filter(
                date_day=date).count()
            for date in dates
        ]

        # Добавить временной ряд на график
        trace = go.Scatter(
            x=x_values,
            y=y_values,
            name=app,
            line=dict(),
            mode='lines+markers',
        )
        data.append(trace)

    # Получить даты, за которые были произведены скачивания игр
    game_dates = Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).annotate(date_day=TruncDate('date')).dates('date_day', 'day')

    # Создать временной ряд для общего количества скачиваний игр
    game_x_values = [d for d in game_dates]
    game_y_values = [
        Downloads.objects.filter(Q(date__gte=start_date) & Q(date__lt=end_date),if_game=if_game).annotate(date_day=TruncDate('date')).filter(date_day=date).count()
        for date in game_dates
    ]

    # Создать макет для графика
    layout = go.Layout(
        title='Скачивания по приложениям',
        xaxis=dict(
            title='Дата',
            tickformat='%Y-%m-%d',
            hoverformat='%Y-%m-%d'
        ),
        yaxis=dict(
            title='Количество скачиваний'
        )
    )

    # Создать график
    fig = go.Figure(data=data, layout=layout)
    plot_time = pyo.plot(fig, auto_open=False, output_type='div')
    return plot_time


def data_save(location_info, user_agent,request,if_game = True):
    if location_info['status'] == 'success':
        continent = location_info['continent']
        continentCode = location_info['continentCode']
        country = location_info['country']
        countryCode = location_info['countryCode']
        region = location_info['region']
        regionName = location_info['regionName']
        city = location_info['city']
        lat = location_info['lat']
        lon = location_info['lon']
        timezone = location_info['timezone']
        org = location_info['org']
        as_info = location_info['as']
        asname = location_info['asname']
        reverse = location_info['reverse']
        mobile = location_info['mobile']
        proxy = location_info['proxy']
        hosting = location_info['hosting']
        ip_address = location_info['query']
        download = Downloads(gate_app=request.path, ip_address=ip_address, user_agent=user_agent, continent=continent,
                             continentCode=continentCode, country=country, countryCode=countryCode, region=region,
                             regionName=regionName, city=city, lat=lat, lon=lon, timezone=timezone, org=org,
                             as_info=as_info, asname=asname, reverse=reverse, mobile=mobile, proxy=proxy,
                             hosting=hosting, if_game=if_game)
        download.save()
    else:
        print('Не получилось вычислить по IP')
        error_msg = location_info['message']
        ip_address = location_info['query']
        print(f"Причина {location_info['query']}: {location_info['message']}")
        download = Downloads(gate_app=request.path, ip_address=ip_address, user_agent=user_agent, error_msg=error_msg, if_game=if_game)
        download.save()
    return 1


def get_location_info(ip_address):
    url = f"http://ip-api.com/json/{ip_address}?fields=66846719"
    response = requests.get(url)
    data = response.json()
    return data


def every(request):
    ip_address = get_ip_address(request)
    user_agent = get_user_agent(request)
    location_info = get_location_info(ip_address)
    if_game = check_if_game(request.path)
    data_save(location_info, user_agent, request, if_game=if_game)
    return serve(request, request.path, settings.STATIC_ROOT)


def home(request):
    ip_address = get_ip_address(request)
    user_agent = get_user_agent(request)
    location_info = get_location_info(ip_address)
    data_save(location_info, user_agent, request, if_game=False)
    context = {
        'all_games': all_games,
    }
    return render(request, 'home.html', context)


def contacts(request):
    ip_address = get_ip_address(request)
    user_agent = get_user_agent(request)
    location_info = get_location_info(ip_address)
    data_save(location_info, user_agent, request, if_game=False)
    return render(request, 'contacts.html')


def stats(request):
    # чтобы игры стали играми, а не игры стали не играми(на всякий случай)
    ip_address = get_ip_address(request)
    user_agent = get_user_agent(request)
    location_info = get_location_info(ip_address)
    data_save(location_info, user_agent, request, if_game=False)
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=1)
        start_date = end_date - datetime.timedelta(days=7)
    # 1 график
    plot_all_games_time = plot_time_all_game(start_date=start_date,end_date=end_date)
    # 2 график
    plot_time = plot_time_each_game(start_date=start_date,end_date=end_date)
    # 3 график
    plot_pie = circle_plot_by_games(start_date=start_date,end_date=end_date)
    # 4 график
    games_by_country = games_group_by_country(start_date=start_date,end_date=end_date)
    # 5 график
    games_by_city = games_group_by_city(start_date=start_date,end_date=end_date)
    # 6 график
    games_by_regionName = games_group_by_regionName(start_date=start_date,end_date=end_date)


    return render(request, 'infographics.html', {
        'plot_time': plot_time,
        'plot_pie':plot_pie,
        'plot_all_games_time':plot_all_games_time,
        'games_by_country':games_by_country,
        'games_by_city': games_by_city,
        'games_by_regionName': games_by_regionName,
        'start_date': start_date,
        'end_date': end_date - datetime.timedelta(days=1),
    })


def stats_no_games(request):
    # чтобы игры стали играми, а не игры стали не играми(на всякий случай)
    ip_address = get_ip_address(request)
    user_agent = get_user_agent(request)
    location_info = get_location_info(ip_address)
    data_save(location_info, user_agent, request, if_game=False)
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=1)
        start_date = end_date - datetime.timedelta(days=7)

    plot_all_no_games_time = plot_time_all_game(if_game=False,start_date=start_date,end_date=end_date)
    # 2 график
    plot_time_no_games = plot_time_each_game(if_game=False,start_date=start_date,end_date=end_date)
    # 3 график
    plot_pie_no_games = circle_plot_by_games(if_game=False,start_date=start_date,end_date=end_date)
    # 4 график
    no_games_by_country = games_group_by_country(if_game = False,start_date=start_date,end_date=end_date)
    # 5 график
    no_games_by_city = games_group_by_city(if_game=False,start_date=start_date,end_date=end_date)
    # 6 график
    no_games_by_regionName = games_group_by_regionName(if_game=False,start_date=start_date,end_date=end_date)

    return render(request, 'infographics_no_games.html', {
        'plot_time_no_games': plot_time_no_games,
        'plot_pie_no_games': plot_pie_no_games,
        'plot_all_no_games_time': plot_all_no_games_time,
        'no_games_by_country':no_games_by_country,
        'no_games_by_city':no_games_by_city,
        'no_games_by_regionName':no_games_by_regionName,
        'start_date': start_date,
        'end_date': end_date - datetime.timedelta(days=1),
    })

def create_index():
    import sqlite3
    from myapp.auth_meilisearch import client as meili_client
    connection = sqlite3.connect('../db.sqlite3')
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0]) 

    cursor.execute("SELECT id, title, description, url, image, resource_pack, tags FROM myapp_gates;")
    rows = cursor.fetchall()
    
    index = meili_client.index('gates')

    counter = 0
    for row in rows:
        doc = {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'url': row[3],
            'image': row[4],
            'resource_pack': row[5]
        }
        print(f'{row[0]}\n{row[1]}\n{row[2]}')
        print('###############################################')
        
        
        index.add_documents(doc)
    
    
    synonyms = {
    'game': ['play'],
    'play': ['game'],
    }
    index.update_synonyms(synonyms)
    index.update_settings({
    'filterableAttributes': [
      'title',
      'description'
    ],
    'sortableAttributes': [
        'title',
        'description'
    ],
    'searchableAttributes': [
        'title',
        'description'
    ]
    })