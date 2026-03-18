# main.py
"""
Консольное приложение: Информация о странах и погода через Open-Meteo.
Без демо-заглушек — только реальные запросы к API.
"""

import requests
import sys
from colorama import Fore, Style, init
from formatter import format_country_info, format_openmeteo_weather, format_error

# Инициализация colorama
init(autoreset=True)

# Конфигурация API
API_CONFIG = {
    'countries': {
        'base_url': 'https://restcountries.com/v3.1/name/',
        'timeout': 10
    },
    'geocoding': {
        'base_url': 'https://geocoding-api.open-meteo.com/v1/search',
        'timeout': 8
    },
    'weather': {
        'base_url': 'https://api.open-meteo.com/v1/forecast',
        'timeout': 10
    }
}


def print_header():
    """Выводит приветственное сообщение."""
    print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  🌍  Country & Weather Info (Open-Meteo)  🌤️  {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}\n")


def get_user_input(prompt: str, choices: list = None) -> str:
    """
    Получает ввод от пользователя с опциональной валидацией.
    """
    while True:
        user_input = input(f"{Fore.WHITE}{prompt}{Style.RESET_ALL}").strip()
        if not user_input:
            print(format_error("Ввод не может быть пустым", "warning"))
            continue
        if choices and user_input.lower() not in [c.lower() for c in choices]:
            print(format_error(f"Выберите один из вариантов: {', '.join(choices)}", "warning"))
            continue
        return user_input


def fetch_country_info(country_name: str) -> dict:
    """
    Запрашивает информацию о стране из REST Countries API.
    """
    url = f"{API_CONFIG['countries']['base_url']}{country_name}"
    params = {
        'fullText': 'false',
        'fields': 'name,capital,population,area,languages,currencies,region,subregion,timezones,latlng,flag,maps'
    }

    try:
        print(f"{Fore.BLUE}🔄 Загрузка данных о стране...{Style.RESET_ALL}")
        response = requests.get(url, params=params, timeout=API_CONFIG['countries']['timeout'])

        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        elif response.status_code == 404:
            return {'success': False, 'error': f"Страна '{country_name}' не найдена", 'type': 'not_found'}
        else:
            return {'success': False, 'error': f"Ошибка сервера: {response.status_code}", 'type': 'server'}

    except requests.exceptions.Timeout:
        return {'success': False, 'error': "Превышено время ожидания ответа", 'type': 'timeout'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': "Ошибка подключения к серверу", 'type': 'connection'}
    except Exception as e:
        return {'success': False, 'error': f"Неизвестная ошибка: {str(e)}", 'type': 'unknown'}


def geocode_location(location_name: str, country_code: str = None) -> dict:
    """
    Преобразует название локации в координаты через Open-Meteo Geocoding API.

    Args:
        location_name: Название города/страны
        country_code: Код страны (опционально, для уточнения поиска)

    Returns:
        Словарь с координатами или ошибкой
    """
    url = API_CONFIG['geocoding']['base_url']
    params = {
        'name': location_name,
        'count': 1,  # Возвращаем только лучший результат
        'language': 'ru',
        'format': 'json'
    }

    if country_code:
        params['country'] = country_code

    try:
        print(f"{Fore.BLUE}📍 Поиск координат для '{location_name}'...{Style.RESET_ALL}")
        response = requests.get(url, params=params, timeout=API_CONFIG['geocoding']['timeout'])

        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                return {
                    'success': True,
                    'latitude': result['latitude'],
                    'longitude': result['longitude'],
                    'name': result.get('name', location_name),
                    'country': result.get('country', '')
                }
            else:
                return {'success': False, 'error': f"Локация '{location_name}' не найдена", 'type': 'not_found'}
        else:
            return {'success': False, 'error': f"Ошибка геокодинга: {response.status_code}", 'type': 'server'}

    except Exception as e:
        return {'success': False, 'error': f"Ошибка геокодинга: {str(e)}", 'type': 'unknown'}


def fetch_weather_info(latitude: float, longitude: float, location_name: str) -> dict:
    """
    Запрашивает данные о погоде через Open-Meteo API.

    Args:
        latitude: Широта
        longitude: Долгота
        location_name: Название локации для отображения

    Returns:
        Словарь с данными о погоде или ошибкой
    """
    url = API_CONFIG['weather']['base_url']
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m',
        'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum',
        'timezone': 'auto',
        'forecast_days': 1
    }

    try:
        print(f"{Fore.BLUE}🌤️  Загрузка прогноза погоды...{Style.RESET_ALL}")
        response = requests.get(url, params=params, timeout=API_CONFIG['weather']['timeout'])

        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'data': data,
                'location_name': location_name
            }
        else:
            return {'success': False, 'error': f"Ошибка погодного API: {response.status_code}", 'type': 'server'}

    except requests.exceptions.Timeout:
        return {'success': False, 'error': "Превышено время ожидания погоды", 'type': 'timeout'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': "Нет подключения к погодному сервису", 'type': 'connection'}
    except Exception as e:
        return {'success': False, 'error': f"Ошибка погоды: {str(e)}", 'type': 'unknown'}


def main_menu(country: str, country_code: str = None):
    """
    Главное меню после выбора страны.
    """
    while True:
        print(f"\n{Fore.CYAN}📋 Меню: {Fore.WHITE}{country.title()}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Информация о стране")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Погода (через Open-Meteo)")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Выбрать другую страну")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Выход")

        choice = get_user_input("\nВаш выбор (1-4): ", ['1', '2', '3', '4'])

        if choice == '1':
            result = fetch_country_info(country)
            if result['success']:
                print(format_country_info(result['data']))
            else:
                print(format_error(result['error'], result.get('type', 'error')))

        elif choice == '2':
            # Сначала получаем координаты через геокодинг
            geo_result = geocode_location(country, country_code)

            if geo_result['success']:
                # Затем запрашиваем погоду по координатам
                weather_result = fetch_weather_info(
                    geo_result['latitude'],
                    geo_result['longitude'],
                    geo_result['name']
                )

                if weather_result['success']:
                    print(format_openmeteo_weather(
                        weather_result['data'],
                        weather_result['location_name']
                    ))
                else:
                    print(format_error(weather_result['error'], weather_result.get('type', 'error')))
            else:
                print(format_error(geo_result['error'], geo_result.get('type', 'error')))
                # Предложить ввести город вручную
                manual_city = get_user_input("🏙️  Введите название города вручную: ").strip()
                if manual_city:
                    geo_result = geocode_location(manual_city)
                    if geo_result['success']:
                        weather_result = fetch_weather_info(
                            geo_result['latitude'],
                            geo_result['longitude'],
                            geo_result['name']
                        )
                        if weather_result['success']:
                            print(format_openmeteo_weather(
                                weather_result['data'],
                                weather_result['location_name']
                            ))
                        else:
                            print(format_error(weather_result['error'], weather_result.get('type', 'error')))
                    else:
                        print(format_error(geo_result['error'], "error"))

        elif choice == '3':
            return 'change_country'

        elif choice == '4':
            print(f"\n{Fore.GREEN}👋 Спасибо за использование! До свидания!{Style.RESET_ALL}\n")
            return 'exit'


def country_selection():
    """Меню выбора страны."""
    print(f"{Fore.GREEN}💡 Вводите название страны на английском{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   Примеры: Russia, Germany, Japan, Brazil, Uzbekistan{Style.RESET_ALL}\n")

    while True:
        country = get_user_input("🌍 Название страны: ")

        print(f"\n{Fore.CYAN}🔍 Проверка...{Style.RESET_ALL}")
        test_result = fetch_country_info(country)

        if test_result['success']:
            country_data = test_result['data'][0]
            country_name = country_data.get('name', {}).get('common', country)
            country_code = country_data.get('cca2', '').lower()
            capital = country_data.get('capital', [None])[0]

            print(f"{Fore.GREEN}✅ Найдена: {country_name}{Style.RESET_ALL}")
            if capital:
                print(f"{Fore.CYAN}🏙️  Столица: {capital} (будет использована для погоды){Style.RESET_ALL}")

            return country.lower(), country_code, capital or country_name
        else:
            print(format_error(test_result['error'], "warning"))
            retry = get_user_input("Попробовать снова? (y/n): ", ['y', 'n', 'yes', 'no'])
            if retry.lower() in ['n', 'no']:
                return None, None, None


def main():
    """Точка входа в приложение."""
    print_header()

    while True:
        country, country_code, location_for_weather = country_selection()
        if not country:
            print(f"{Fore.YELLOW}⚠️  Завершение работы.{Style.RESET_ALL}")
            break

        action = main_menu(country, country_code)
        if action == 'exit':
            break

    print(f"\n{Fore.CYAN}{'▁' * 60}{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Прервано пользователем{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(format_error(f"Критическая ошибка: {str(e)}", "error"))
        sys.exit(1)