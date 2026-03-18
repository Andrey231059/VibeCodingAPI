# formatter.py
"""
Модуль для преобразования JSON-ответов в читаемый консольный формат.
Использует colorama для цветного вывода.
"""

from colorama import Fore, Style, init
import json
from typing import Dict, List, Any

# Инициализация colorama для кроссплатформенной работы
init(autoreset=True)


def format_country_info(data: List[Dict[str, Any]]) -> str:
    """
    Форматирует информацию о стране из REST Countries API.

    Args:
        data: Список словарей с данными о стране (обычно 1 элемент)

    Returns:
        Отформатированная строка для вывода в консоль
    """
    if not data:
        return f"{Fore.RED}❌ Страна не найдена{Style.RESET_ALL}"

    country = data[0]
    result = []

    # Заголовок
    name = country.get('name', {}).get('common', 'N/A')
    result.append(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    result.append(f"{Fore.CYAN}🌍 {name.upper()}{Style.RESET_ALL}")
    result.append(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")

    # Основная информация
    info = [
        ("🏛️ Официальное название", country.get('name', {}).get('official', 'N/A')),
        ("🗣️ Языки", ', '.join(country.get('languages', {}).values()) if country.get('languages') else 'N/A'),
        ("💱 Валюта", ', '.join(f"{curr['name']} ({curr['symbol']})"
                               for curr in country.get('currencies', {}).values())
        if country.get('currencies') else 'N/A'),
        ("👥 Население", f"{country.get('population', 0):,}"),
        ("🌐 Регион", country.get('region', 'N/A')),
        ("🗺️ Субрегион", country.get('subregion', 'N/A')),
        ("📏 Площадь", f"{country.get('area', 0):,} км²" if country.get('area') else 'N/A'),
        ("🕐 Часовые пояса", ', '.join(country.get('timezones', [])) if country.get('timezones') else 'N/A'),
    ]

    for label, value in info:
        result.append(f"{Fore.GREEN}{label}:{Style.RESET_ALL} {Fore.WHITE}{value}{Style.RESET_ALL}")

    # Столица и координаты
    capital = country.get('capital', ['N/A'])[0] if country.get('capital') else 'N/A'
    lat = country.get('latlng', [None, None])[0]
    lng = country.get('latlng', [None, None])[1]
    coords = f"{lat}, {lng}" if lat and lng else 'N/A'

    result.append(f"\n{Fore.GREEN}🏙️ Столица:{Style.RESET_ALL} {Fore.WHITE}{capital}{Style.RESET_ALL}")
    result.append(f"{Fore.GREEN}📍 Координаты:{Style.RESET_ALL} {Fore.WHITE}{coords}{Style.RESET_ALL}")

    # Флаг (эмодзи или ссылка)
    flag = country.get('flag', '🏁')
    result.append(f"{Fore.GREEN}🚩 Флаг:{Style.RESET_ALL} {Fore.WHITE}{flag}{Style.RESET_ALL}")

    # Ссылки
    if country.get('maps', {}).get('googleMaps'):
        result.append(f"\n{Fore.BLUE}🔗 Google Maps:{Style.RESET_ALL} {country['maps']['googleMaps']}")

    result.append(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

    return '\n'.join(result)


def format_weather_info(data: Dict[str, Any]) -> str:
    """
    Форматирует данные о погоде (универсальный формат).

    Args:
        data: Словарь с данными о погоде

    Returns:
        Отформатированная строка для вывода в консоль
    """
    if not data:
        return f"{Fore.RED}❌ Не удалось получить данные о погоде{Style.RESET_ALL}"

    result = []
    result.append(f"\n{Fore.YELLOW}{'☁️' * 25}{Style.RESET_ALL}")
    result.append(f"{Fore.YELLOW}🌤️  ПРОГНОЗ ПОГОДЫ{Style.RESET_ALL}")
    result.append(f"{Fore.YELLOW}{'☁️' * 25}{Style.RESET_ALL}\n")

    # Попытка извлечь стандартные поля (адаптируйте под реальный API)
    fields = [
        ("📍 Локация", data.get('location', data.get('name', 'N/A'))),
        ("🌡️ Температура", f"{data.get('temperature', data.get('temp', 'N/A'))}°C"),
        ("💧 Влажность", f"{data.get('humidity', 'N/A')}%"),
        ("💨 Ветер", f"{data.get('wind_speed', data.get('wind', 'N/A'))} м/с"),
        ("🔍 Описание", data.get('description', data.get('weather', 'N/A')).capitalize()),
        ("⏰ Время обновления", data.get('last_updated', 'N/A')),
    ]

    for label, value in fields:
        if value != 'N/A' or label == "🔍 Описание":  # Показывать только заполненные поля
            result.append(f"{Fore.GREEN}{label}:{Style.RESET_ALL} {Fore.WHITE}{value}{Style.RESET_ALL}")

    # Если данные в неизвестном формате — показать сырой JSON (для отладки)
    if len(result) <= 4:  # Только заголовок
        result.append(f"\n{Fore.LIGHTBLACK_EX}📋 Сырые данные:{Style.RESET_ALL}")
        result.append(f"{Fore.LIGHTBLACK_EX}{json.dumps(data, indent=2, ensure_ascii=False)}{Style.RESET_ALL}")

    result.append(f"\n{Fore.YELLOW}{'☁️' * 25}{Style.RESET_ALL}")

    return '\n'.join(result)


def format_error(message: str, error_type: str = "error") -> str:
    """
    Форматирует сообщение об ошибке.

    Args:
        message: Текст ошибки
        error_type: Тип ошибки ('error', 'warning', 'info')

    Returns:
        Цветная строка с ошибкой
    """
    colors = {
        'error': Fore.RED,
        'warning': Fore.YELLOW,
        'info': Fore.BLUE
    }
    icons = {
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    color = colors.get(error_type, Fore.RED)
    icon = icons.get(error_type, '❌')

    return f"\n{color}{icon} {message}{Style.RESET_ALL}\n"


# formatter.py — ДОБАВЬТЕ ЭТУ ФУНКЦИЮ в конец файла

def format_openmeteo_weather(data: dict, location_name: str = "") -> str:
    """
    Форматирует ответ от Open-Meteo API в читаемый консольный вид.

    Args:
        data: Словарь с ответом Open-Meteo
        location_name: Название локации для заголовка

    Returns:
        Отформатированная строка с цветным выводом
    """
    from colorama import Fore, Style

    if not data or 'current' not in data:
        return f"{Fore.RED}❌ Нет данных о погоде{Style.RESET_ALL}"

    current = data['current']
    daily = data.get('daily', {})

    # Расшифровка weather_code (WMO code)
    weather_codes = {
        0: "☀️ Ясно", 1: "🌤️ Преим. ясно", 2: "⛅ Переменная облачность",
        3: "☁️ Пасмурно", 45: "🌫️ Туман", 48: "🌫️ Туман с изморозью",
        51: "🌦️ Слабая морось", 53: "🌦️ Морось", 55: "🌧️ Плотная морось",
        61: "🌧️ Слабый дождь", 63: "🌧️ Дождь", 65: "🌧️ Сильный дождь",
        71: "🌨️ Слабый снег", 73: "🌨️ Снег", 75: "❄️ Сильный снег",
        80: "🌦️ Ливень", 95: "⛈️ Гроза", 96: "⛈️ Гроза с градом"
    }

    weather_text = weather_codes.get(current.get('weather_code'), "🌡️ Неизвестно")

    result = []
    result.append(f"\n{Fore.YELLOW}{'☁️' * 25}{Style.RESET_ALL}")
    result.append(f"{Fore.YELLOW}🌤️  ПОГОДА: {location_name.upper()}{Style.RESET_ALL}")
    result.append(f"{Fore.YELLOW}{'☁️' * 25}{Style.RESET_ALL}\n")

    # Текущие условия
    current_info = [
        ("🌡️ Температура", f"{current.get('temperature_2m', 'N/A')}°C"),
        ("🤔 Ощущается как", f"{current.get('apparent_temperature', 'N/A')}°C"),
        ("💧 Влажность", f"{current.get('relative_humidity_2m', 'N/A')}%"),
        ("💨 Ветер", f"{current.get('wind_speed_10m', 'N/A')} м/с"),
        ("🧭 Направление ветра", f"{current.get('wind_direction_10m', 'N/A')}°"),
        ("🌧️ Осадки", f"{current.get('precipitation', 0)} мм"),
        ("🔍 Условия", weather_text),
        ("⏰ Время данных", current.get('time', 'N/A').replace('T', ' ')),
    ]

    for label, value in current_info:
        result.append(f"{Fore.GREEN}{label}:{Style.RESET_ALL} {Fore.WHITE}{value}{Style.RESET_ALL}")

    # Прогноз на день (макс/мин температура)
    if daily.get('temperature_2m_max') and daily.get('temperature_2m_min'):
        t_max = daily['temperature_2m_max'][0] if daily['temperature_2m_max'] else None
        t_min = daily['temperature_2m_min'][0] if daily['temperature_2m_min'] else None
        if t_max is not None and t_min is not None:
            result.append(f"\n{Fore.CYAN}📊 Прогноз на сегодня:{Style.RESET_ALL}")
            result.append(f"{Fore.WHITE}  Макс: {t_max}°C  |  Мин: {t_min}°C{Style.RESET_ALL}")

    # Ссылка на источник
    result.append(f"\n{Fore.BLUE}🔗 Источник: open-meteo.com{Style.RESET_ALL}")
    result.append(f"{Fore.YELLOW}{'☁️' * 25}{Style.RESET_ALL}")

    return '\n'.join(result)