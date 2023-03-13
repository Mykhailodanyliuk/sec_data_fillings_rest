import json
import os
import shutil
import time
from zipfile import ZipFile

import requests


def download_file_requests(url, path_to_file):
    try:
        response = requests.get(url)
        open(path_to_file, "wb").write(response.content)
    except Exception as e:
        print(e)
        time.sleep(60)
        download_file_requests(url, path_to_file)


def delete_directory(path_to_directory):
    if os.path.exists(path_to_directory):
        shutil.rmtree(path_to_directory)


def create_directory(path_to_dir, name):
    mypath = f'{path_to_dir}/{name}'
    if not os.path.isdir(mypath):
        os.makedirs(mypath)


def upload_sec_fillings_data(collection_rest_url):
    current_directory = os.getcwd()
    directory_name = 'sec'
    path_to_directory = f'{current_directory}/{directory_name}'
    delete_directory(path_to_directory)
    create_directory(current_directory, directory_name)
    path_to_zip = f'{path_to_directory}/submissions.zip'
    download_file_requests('https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip', path_to_zip)
    with ZipFile(path_to_zip, 'r') as zip:
        zip_files = zip.namelist()
        zip_files = [file[3:13] for file in zip_files if len(file) == 18]
        zip_files = [f'CIK{file}.json' for file in zip_files]
        for file in zip_files:
            response = requests.get(f'{collection_rest_url}?cik={file[3:13]}')
            if response.status_code == 200:
                response_json = json.loads(response.text)
                is_in_database = False if response_json.get('total') == 0 else True
                if not is_in_database:
                    zip.extract(file, path=path_to_directory, pwd=None)
                    with open(f'{path_to_directory}/{file}', 'r') as json_file:
                        data = json.load(json_file)
                    requests.post(f'{collection_rest_url}', json=data)
    delete_directory(path_to_directory)


if __name__ == '__main__':
    rest_col_url = 'http://62.216.33.167:21005/api/sec_data_fillings'
    while True:
        start_time = time.time()
        upload_sec_fillings_data(rest_col_url)
        work_time = int(time.time() - start_time)
        print(work_time)
        print(14400 - work_time)
        time.sleep(14400 - work_time)
