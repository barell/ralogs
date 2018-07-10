#!/usr/bin/env python3

import requests
import aiohttp
import asyncio
import sys
from pathlib import Path
import os
import json


def validate_conf_string(string, key):
    if not string:
        print('Error: ' + key + ' must be configured')
        sys.exit()


def get_config_file():
    return str(Path.home()) + '/.ralogs'


def get_config_value(key):
    data = open(get_config_file()).read()
    config = json.loads(data)

    return config[key]


def fetch_data(path, method='get'):
    rancher_domain = get_config_value('rancher_domain')
    api_key = get_config_value('api_key')
    api_secret = get_config_value('api_secret')

    validate_conf_string(rancher_domain, 'rancher_domain')
    validate_conf_string(api_key, 'api_key')
    validate_conf_string(api_secret, 'api_secret')

    auth = (api_key, api_secret)
    rancher_url = 'http'

    if get_config_value('use_ssl'):
        rancher_url += 's'

    rancher_url += '://' + rancher_domain

    if method == 'get':
        r = requests.get(rancher_url + '/v2-beta/' + path, auth=auth)
    else:
        r = requests.post(rancher_url + '/v2-beta/' + path, auth=auth)

    return r.json()


def get_project_by_name(name):
    response = None

    data = fetch_data('projects')

    for project in data['data']:
        if name == project['name']:
            response = project

    return response


def get_stack_by_name(name, project_id):
    response = None

    data = fetch_data('projects/' + project_id + '/stacks')

    for stack in data['data']:
        if name == stack['name']:
            response = stack

    return response


def get_service_by_id(service_id, project_id):
    return fetch_data('projects/' + project_id + '/services/' + service_id)


async def setup(container_ids, project_id):
    rancher_domain = get_config_value('rancher_domain')
    session = aiohttp.ClientSession()
    loop = asyncio.get_event_loop()

    for container_id in container_ids:
        data = fetch_data('projects/' + project_id + '/containers/' + container_id + '/?action=logs', 'post')
        loop.create_task(serve('wss://' + rancher_domain + '/v1/logs/?token=' + data['token'], session))
        print('Connected to ' + container_id)


async def serve(url, session):
    async with session.ws_connect(url) as ws:
        async for msg in ws:
            print(msg.data)


def main():
    config_file = get_config_file()

    if not os.path.isfile(config_file):
        with open(config_file, 'w') as outfile:
            config = {
                'api_key': '',
                'api_secret': '',
                'rancher_domain': '',
                'use_ssl': True,
            }
            json.dump(config, outfile, sort_keys=True, indent=4)

    if len(sys.argv) < 3:
        print('Usage: ralogs ENVIRONMENT STACK')
        sys.exit()

    project_name = sys.argv[1]
    stack_name = sys.argv[2]
    container_ids = []

    print('Loading stack data for ' + project_name + ' ' + stack_name)
    project = get_project_by_name(project_name)

    if project is None:
        print('Could not find environment named ' + project_name)
        sys.exit()

    stack = get_stack_by_name(stack_name, project['id'])

    if stack is None:
        print('Could not find stack named ' + stack_name)
        sys.exit()

    print('Resolving container IDs...')
    for service_id in stack['serviceIds']:
        service = get_service_by_id(service_id, project['id'])
        container_ids.extend(service['instanceIds'])

    print('OK: ', container_ids)

    print('Connecting...')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup(container_ids, project['id']))
    loop.run_forever()


if __name__ == "__main__":
    main()
