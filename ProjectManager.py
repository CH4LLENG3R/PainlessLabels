from __future__ import print_function

import os
import os.path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from PIL import Image
from tqdm import tqdm
from typing import List, Dict
import shutil
from configparser import ConfigParser

SCOPES = ['https://www.googleapis.com/auth/drive']


class ProjectManager:
    @staticmethod
    def __write_bytesio_to_file(filename, bytesio):
        """
        Write the contents of the given BytesIO to a file.
        Creates the file or overwrites the file if it does
        not exist yet.
        """
        with open(filename, "wb") as outfile:
            # Copy the BytesIO stream to the output file
            outfile.write(bytesio.getbuffer())

    @staticmethod
    def get_creds():
        flow = InstalledAppFlow.from_client_secrets_file(
            'cred.json', SCOPES)
        creds = flow.run_local_server(port=0)
        return creds

    @staticmethod
    def update_creds() -> Credentials:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as e:
                    os.remove('token.json')
                    creds = ProjectManager.get_creds()
            else:
                creds = ProjectManager.get_creds()
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def download_folder(self, folder_to_download, output_folder):
        subfolders = folder_to_download.split("/")

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = ProjectManager.update_creds()

        items = []
        try:
            self.__service = build('drive', 'v3', credentials=creds)

            # Call the Drive v3 API
            results = self.__service.files().list(
                q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(subfolders[0]),
                fields="nextPageToken, files(id, name)").execute()
            folder_id = results.get('files', [])[0]['id']

            for subfolder in subfolders[1:]:
                results = self.__service.files().list(
                    q="'{}' in parents and name='{}' and mimeType='application/vnd.google-apps.folder'".format(
                        folder_id, subfolder), fields="nextPageToken, files(id, name)").execute()
                folder_id = results.get('files', [])[0]['id']

            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = self.__service.files().list(
                    q="'{}' in parents and mimeType!='application/vnd.google-apps.folder'".format(folder_id),
                    spaces='drive',
                    fields='nextPageToken, '
                           'files(id, name)',
                    pageToken=page_token).execute()
                for file in response.get('files', []):
                    # Process change
                    print(F'Found file: {file.get("name")}, {file.get("id")}')
                items.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

            if not items:
                print('No files found.')
                return

            print('downloading...')
            for item in tqdm(items):
                if os.path.exists(output_folder + item['name']):
                    continue

                # download
                request = self.__service.files().get_media(fileId=item['id'])
                file = io.BytesIO()
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                ProjectManager.__write_bytesio_to_file(output_folder + "/" + item['name'], file)
                print(u'{0} ({1})'.format(item['name'], item['id']))
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            # TODO(Guy who wrote this example) - Don't tell me what to do.
            print(f'An error occurred: {error}')

    def get_project_folders(self) -> List[Dict[str, str]]:
        res = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = self.__service.files().list(
                q="name contains \"#PL_\" and mimeType='application/vnd.google-apps.folder' and trashed = false",
                spaces='drive',
                fields='nextPageToken, '
                       'files(id, name)',
                pageToken=page_token).execute()
            res.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        res = [i for i in res if i['name'].startswith('#PL_')]
        return res

    def __choose_project(self, res: List[Dict[str, str]]) -> Dict[str, str]:
        print('Choose Project')
        if len(res) == 0:
            print("No projects found.")
            input("Press Enter to continue...")
            raise Exception('No projects found.')

        for i in range(0, len(res)):
            print(f'{i + 1}: {res[i]["name"]}')
        choice = int(input("choice: ")) - 1
        if 0 <= int(choice) <= len(res):
            return res[int(choice)]

    def __get_availible_subsets(self, ):
        res = []
        page_token = None
        results = self.__service.files().list(
            q=f"'{self.__project['id']}' in parents"
              f" and name='dataset'"
              f" and mimeType='application/vnd.google-apps.folder'", fields="nextPageToken, files(id, name)").execute()
        data_subfolder_id = results.get('files', [])[0]['id']
        while True:
            # pylint: disable=maybe-no-member
            response = self.__service.files().list(
                q=f"'{data_subfolder_id}' in parents"
                  f" and mimeType='application/vnd.google-apps.folder'"
                  f" and trashed = false",
                spaces='drive',
                fields='nextPageToken, '
                       'files(id, name)',
                pageToken=page_token).execute()
            res.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        res = sorted([i for i in res if i['name'].startswith('subset_')], key=lambda d: d['name'])
        return res

    def __choose_subset(self, res: List[Dict[str, str]]) -> Dict[str, str]:
        print('Choose Subset to download')
        if len(res) == 0:
            print("No subsets found.")
            input("Press Enter to continue...")
            raise Exception('No subsets found.')

        for i in range(0, len(res)):
            print(f'{i + 1}: {res[i]["name"]}')
        choice = int(input("choice: ")) - 1
        if 0 <= int(choice) <= len(res):
            return res[int(choice)]

    def __download_config(self):
        items = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = self.__service.files().list(
                q=f"'{self.__project['id']}' in parents "
                  "and name='config.ini' "
                  "and mimeType!='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='nextPageToken, '
                       'files(id, name)',
                pageToken=page_token).execute()
            items.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        item = None
        for item in items:
            if item['name'] == 'config.ini':
                break
        if item is None:
            print("No config.ini file found")
            input('Press Enter to continue...')
        # download
        request = self.__service.files().get_media(fileId=item['id'])
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        ProjectManager.__write_bytesio_to_file(self.__config_path + '/config.ini', file)

    def __download_item(self, item):
        request = self.__service.files().get_media(fileId=item['id'])
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        ProjectManager.__write_bytesio_to_file(self.__data_path + '/' + item['name'], file)

    @staticmethod
    def __validate_img(path: str) -> bool:
        try:
            img = Image.open(path)  # open the image file
            img.verify()  # verify that it is, in fact an image
        except (IOError, SyntaxError) as e:
            return False
        return True

    def __download_data(self, subset: Dict[str, str]):
        items = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = self.__service.files().list(
                q=f"'{subset['id']}' in parents and mimeType!='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='nextPageToken, '
                       'files(id, name)',
                pageToken=page_token).execute()
            items.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        if not items:
            raise ResourceWarning(f'No files found in subset: {subset["name"]}')

        print('downloading...')
        for item in tqdm(items):
            # retry downloading if image is broken
            for i in range(0, 2):
                self.__download_item(item)
                if ProjectManager.__validate_img(self.__data_path + '/' + item['name']):
                    break
                print(f'File {item["name"]} was corrupted.')

    def upload_result(self, project: str):
        print('Upload pending...')
        f = open(f'sources/{project}/config/driveConfig.cnf', 'r')
        subset_name = f.readline()
        f.close()

        projects = self.get_project_folders()
        project_folder = None
        for project_folder in projects:
            if project_folder['name'] == project:
                break

        results = self.__service.files().list(
            q=f"'{project_folder['id']}' in parents"
              f" and name='output'"
              f" and mimeType='application/vnd.google-apps.folder'", fields="nextPageToken, files(id, name)").execute()
        output_subfolder_id = results.get('files', [])[0]['id']

        file_metadata = {'name': subset_name + '.csv',
                         "parents": [output_subfolder_id]
                         }
        media = MediaFileUpload(f'sources/{project}/output/output.csv',
                                mimetype=None)
        file = self.__service.files().create(body=file_metadata,
                                             media_body=media,
                                             fields='id').execute()
        print('Done. You can close this window.')

    @staticmethod
    def __create_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def __create_enviroment(self):
        project_full_path = f'sources/{self.__project_name}'
        self.__config_path = os.path.join(project_full_path, 'config')
        self.__data_path = os.path.join(project_full_path, 'data')
        self.__output_path = os.path.join(project_full_path, 'output')

        ProjectManager.__create_folder(project_full_path)
        ProjectManager.__create_folder(self.__config_path)
        ProjectManager.__create_folder(self.__data_path)
        ProjectManager.__create_folder(self.__output_path)

    def download_new(self):
        projects = self.get_project_folders()
        self.__project = self.__choose_project(projects)
        self.__project_name = self.__project['name']
        if os.path.exists(f'sources/{self.__project_name}'):
            shutil.rmtree(f'sources/{self.__project_name}')
        subsets = self.__get_availible_subsets()
        self.__subset = self.__choose_subset(subsets)
        self.__subset_name = self.__subset['name']
        self.__create_enviroment()
        self.__download_config()
        self.__download_data(self.__subset)
        f = open(self.__config_path + '/driveConfig.cnf', 'w')
        f.write(self.__subset['name'])
        f.close()

    def __init__(self):
        self.__subset = None
        self.__project = None
        self.__project_name = None
        self.__subset_name = None
        creds = ProjectManager.update_creds()
        self.__service = build('drive', 'v3', credentials=creds)

    def create_copy(self):
        config = ConfigParser()
        config.read(f'sources/{self.__project_name}/config/config.ini')
        paths = config['paths']
        output_path = paths['output_path']
        if not os.path.isdir('saves'):
            os.mkdir('saves')
        shutil.copyfile(output_path, f'saves/{self.__project_name}_{self.__subset_name}_output.csv')

    def get_project_name(self):
        return self.__project_name

    def choose_from_existing(self) -> str:
        if not (os.path.exists('sources') and len(os.listdir('sources')) > 0):
            print('no local projects yet.')
            input('Press Enter to continue...\n')
            return ''

        local_projects = os.listdir('sources')

        for i in range(0, len(local_projects)):
            print(f'{i + 1}: {local_projects[i]}')
        while True:
            choice = int(input('choice: '))
            if 1 <= choice <= len(local_projects) + 1:
                self.__project_name = local_projects[choice - 1]
                f = open(f'sources/{self.__project_name}/config/driveConfig.cnf', 'r')
                self.__subset_name = f.readline().replace('\n', '')
                f.close()
                return self.__project_name
            print('incorrect choice.')
