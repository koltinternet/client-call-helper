import sys
from urllib import parse as urllib_parse
import requests

HYDRA_URL = 'https://h.billing.ru'
HYDRA_USER = 'pooruser'
HYDRA_PASSWORD = 'badpassowrd'

API_URL = f'{HYDRA_URL}/rest/v2/'
USER_EDIT_URL = f'{HYDRA_URL}/subjects/users/edit/'
TOKEN_FILE = '.token'


def save_token(token: str) -> None:
    with open(TOKEN_FILE, 'w') as file:
        file.write(token)


def load_token() -> str:
    try:
        with open(TOKEN_FILE) as file:
            return file.read()
    except FileNotFoundError:
        return None


def get_auth_token(user: str = HYDRA_USER, password: str = HYDRA_PASSWORD, timeout: int = 60) -> str:
    auth_url = urllib_parse.urljoin(API_URL, 'login')
    auth_params = {'session': {'login': user, 'password': password}}
    try:
        response = requests.post(auth_url, json=auth_params, timeout=timeout)
        response.raise_for_status()  # Поднимет исключение при ошибке HTTP
        return response.json()['session']['token']
    except requests.RequestException as e:
        print(f"Error during authentication: {e}")
        sys.exit(1)


def hydra_request(auth_token: str, url: str, params: dict, method: str = 'get', timeout: int = 60) -> dict:
    full_url = urllib_parse.urljoin(API_URL, url)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Token token={auth_token}',
    }

    try:
        response = requests.request(method, full_url, headers=headers, timeout=timeout,
                                    **({'params': params} if method == 'get' else {'json': params}))
        response.raise_for_status()  # Поднимет исключение при ошибке HTTP
        return response.json()
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return {'error': str(e)}


def get_addresses_by_phone(auth_token: str, phone: str) -> dict:
    search_data = hydra_request(auth_token, 'search', {'result_subtype_id': '2001', 'query': phone})
    if not search_data or not search_data.get('search_results'):
        return search_data
    user_id = search_data['search_results'][0]['n_result_id']

    customer_data = hydra_request(auth_token, 'subjects/customers/batch', {'ids': [user_id]}, 'post')
    user_base_id = customer_data['customers'][0]['n_base_subject_id']
    user_name = customer_data['customers'][0]['vc_base_subject_name']

    addresses = []
    address_data = hydra_request(auth_token, 'subject_addresses', {'subject_id': [user_base_id]})
    for addr in address_data.get('subject_addresses', []):
        addresses.append({'addr_type_id': addr['n_addr_type_id'], 'vc_visual_code': addr['vc_visual_code']})

    return {
        'user_id': user_id,
        'user_name:': user_name,
        'user_url': f'{USER_EDIT_URL}{user_id}',
        'addresses': addresses
    }


def main():
    for _ in range(3):
        auth_token = load_token()
        if not auth_token:
            auth_token = get_auth_token()
            save_token(auth_token)

        # Поиск по номеру телефона
        result = get_addresses_by_phone(auth_token, phone='79215555555')

        if 'Unauthorized for url' in result.get('error', ''):
            print(result, 'Trying to update token...')
            save_token(get_auth_token())  # Обновляем токен
        else:
            print(result)
            break


if __name__ == '__main__':
    main()