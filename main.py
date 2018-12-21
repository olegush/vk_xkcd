import os
import random
import requests
import json
from dotenv import load_dotenv


def fetch_xkcd_image(args):
    website, url_tail, id = args.values()
    url = '{}/{}/{}'.format(website, id, url_tail)
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data


def download_img(filename, url):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)


def get_vk_server_to_upload(vk_args, method):
    url, token, client_id, group_id, version = vk_args.values()
    url_for_request = '{}/{}'.format(url, method)
    payload = {'access_token': token, 'group_id': group_id, 'v': version}
    response = requests.get(url_for_request, params=payload)
    return json.loads(response.text)


def get_vk_uploaded_data(filename, url):
    file = open(filename, 'rb')
    files = {'photo': file}
    response = requests.post(url, files=files)
    file.close()
    return json.loads(response.text)


def save_vk_img(vk_args, method, server, photo, hash):
    url, token, client_id, group_id, version = vk_args.values()
    url_for_save = '{}/{}'.format(url, method)
    payload = {
        'access_token': token,
        'group_id': group_id,
        'v': version,
        'server':
        server,
        'photo': photo,
        'hash': hash
    }
    response = requests.post(url_for_save, data=payload)
    return json.loads(response.text)


def post_vk_post(vk_args, method, owner_id, photo_id, message, xkcd_args):
    url, token, client_id, group_id, version = vk_args.values()
    xkcd_api, __, comic_id = xkcd_args.values()
    url_for_post = '{}/{}'.format(url, method)
    attachments = 'photo{}_{},{}/{}/'.format(
                                        owner_id,
                                        str(photo_id),
                                        xkcd_api,
                                        comic_id
                                    )
    payload = {
        'access_token': token,
        'owner_id': '-{}'.format(group_id),
        'v': version,
        'from_group': 1,
        'message': message,
        'attachments':
        attachments
    }
    response = requests.post(url_for_post, data=payload)
    return json.loads(response.text)


def remove_img(filename):
    os.remove(filename)


if __name__ == '__main__':
    load_dotenv()
    comic_id = round(random.random() * 2087)
    xkcd_api_args = {
        'url': 'https://xkcd.com',
        'tail': 'info.0.json',
        'comic_id': comic_id
    }
    vk_api_args = {
        'url': 'https://api.vk.com/method',
        'token': os.getenv('TOKEN'),
        'client_id': os.getenv('CLIENT_ID'),
        'group_id': '175493142',
        'version': '5.92'
    }

    print('1. Got random comic ID:{}\n'.format(comic_id))

    xkcd_img_data = fetch_xkcd_image(xkcd_api_args)
    *__, title, img_url, __, __ = xkcd_img_data.values()
    filename = img_url.split('/')[-1]
    print('2. Data from XKCD for comic "{}" was fetched\n'.format(filename))

    download_img(filename, img_url)
    print('3. The comic "{}" was downloaded to current dir\n'.format(filename))

    upload_url = get_vk_server_to_upload(
                    vk_api_args,
                    'photos.getWallUploadServer'
                )['response']['upload_url']
    print('4. Got url to upload on VK server\n')

    vk_uploaded_data = get_vk_uploaded_data(filename, upload_url)
    server, photo, hash = vk_uploaded_data.values()
    print('5. The comic was uploaded on the server {}\n'.format(server))

    vk_saved_data = save_vk_img(
                        vk_api_args,
                        'photos.saveWallPhoto',
                        server,
                        photo,
                        hash
                    )
    photo_id, __, owner_id, *__ = vk_saved_data['response'][0].values()
    print('6. The comic got upload ID:{}\n'.format(photo_id))

    vk_post_data = post_vk_post(
                        vk_api_args,
                        'wall.post',
                        owner_id,
                        photo_id,
                        title,
                        xkcd_api_args
                    )
    print('7. The post published on the wall of the group:{}\n')

    remove_img(filename)
    print('8. Image "{}" successfully removed\n'.format(filename))
