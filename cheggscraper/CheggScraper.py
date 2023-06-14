import json
import logging
import os
import random
import re
import string
from typing import Union, Optional
from typing import Optional, Tuple

import unicodedata
from importlib.resources import read_text

import requests
from requests import Response
from bs4 import BeautifulSoup
from bs4.element import Tag
from jinja2 import Environment, BaseLoader

from .Exceptions import *

logging.basicConfig(filename='scraper.log', filemode='w', level=logging.DEBUG)

main_template = Environment(loader=BaseLoader).from_string(read_text('cheggscraper', 'template.html'))
chapter_type_template = Environment(loader=BaseLoader).from_string(read_text('cheggscraper', 'chapter_type_frame.html'))


class CheggScraper:
    """
    Scrape html from chegg.com and store them in a way so you don't need cookie to view the file
    """

    def __init__(self, cookie: str = None, cookie_path: str = None, user_agent: str = None, base_path: str = None,
                 save_file_format: str = None, config: dict = None, template_path: str = None,
                 extra_header_tag: str = None):

        self.base_path = base_path

        self.save_file_format = save_file_format

        if self.base_path:
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)

        if not self.base_path:
            self.base_path = ''

        self.extra_header_tag = extra_header_tag

        if cookie:
            self.cookie = cookie
        else:
            self.cookie = self.parse_cookie(cookie_path)

        self.cookie_dict = self.cookie_str_to_dict(self.cookie)

        self.template_path = template_path

        if not config:
            config = json.loads(read_text('cheggscraper', 'conf.json'))

        if not user_agent:
            user_agent = config.get('user_agent')
        if not user_agent:
            raise Exception('user_agent not defined')

        logging.debug(msg=f'user_agent: {user_agent}')

        self.user_agent = user_agent

        self.headers = {
            'authority': 'www.chegg.com',
            # 'cache-control': 'max-age=0',
            "Accept-Encoding": "gzip, deflate, br",
            'accept-language': 'en-US,en;q=0.9',
            'cookie': self.cookie,
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'user-agent': self.user_agent,
        }

        self.ajax_url = 'https://www.chegg.com/study/_ajax/enhancedcontent?token={token}&questionUuid={question_uuid}&showOnboarding=&templateName=ENHANCED_CONTENT_V2&deviceFingerPrintId={deviceFingerPrintId}'

        logging.debug(f'self.cookie = {self.cookie}')

        self.deviceFingerPrintId = self.cookie_dict.get('DFID')

    @staticmethod
    def slugify(value: str, allow_unicode: bool = False) -> str:
        """
        slugify the names of files

        :param value: string to be slugify
        :type value: str
        :param allow_unicode: allow unicode
        :type allow_unicode: bool
        :return: string after slugify
        :rtype: str
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '',git init
 value.lower())
        return re.sub(r'[-\s]+', '-',  value).strip('-_')

    @staticmethod
    def render_chapter_type_html(data: dict) -> str:
        """
        Render chapter type answers using data

        :param data: response from graphql url
        :type data: dict
        :return: rendered html code
        :rtype: str
        """
        json_obj = json.dumps(data.json())
        data = json.loads(json_obj)
        #print(data)
        #for key, value in data.items():
        #    print(f"{key}: {value}")

        totalSteps = data['data']['tbsSolutionContent'][0]['totalSteps']
        steps = data["data"]["tbsSolutionContent"][0]["stepsLink"]
        _data = {
            'chapterName': None,
            'problemName': None,
            'problemHtml': None,
            'totalSteps': totalSteps,
            'steps': steps,
        }

        return chapter_type_template.render(**_data)

    @staticmethod
    def replace_src_links(html_text: str) -> str:
        """
        Replace relative links from page, so even you are opening file without any host, still can see all contents,
        still some css and js won't load

        :param html_text: html code of page
        :type html_text: str
        :return: html code after modify all relative links
        :rtype: str
        """
        return re.sub(r'src=\s*?"//(.*)?"', r'src="https://\1"', html_text)

    @staticmethod
    def cookie_str_to_dict(cookie_str: str) -> dict:
        """
        Convert cookie str to dict of key, value pairs

        :param cookie_str: cookie in format of string [key=value; key=value]
        :type cookie_str: str
        :return: dictionary of key value pairs of key value pairs
        :rtype: dict
        """
        ret = {}
        cookie_pairs = cookie_str.split(';')
        for pair in cookie_pairs:
            key, value = pair.split('=', 1)
            key = key.strip()
            value = value.strip()
            ret.update({key: value})
        return ret

    @staticmethod
    def parse_json(json_string: str) -> dict:
        """
        just parse json

        :param json_string: json data in format of string
        :type json_string: str
        :return: dict
        :rtype: dict
        """
        try:
            data = json.loads(json_string)
            return data
        except Exception as e:
            logging.debug(msg=f'::while parsing json: {e}')
            raise JsonParseError

    @staticmethod
    def dict_to_cookie_str(cookie_dict: dict) -> str:
        """
        Convert dict to cookie string

        :param cookie_dict: dictionary of cookie, key value pairs
        :type cookie_dict: dict
        :return: cookie in string format
        :rtype: str
        """
        cookie_str = ''
        first_flag = True
        for cookie in cookie_dict:
            if not first_flag:
                cookie_str += '; '
            cookie_str += '{name}={value}'.format(**cookie)
            first_flag = False
        return cookie_str

    @staticmethod
    def parse_cookie(cookie_path: str) -> str:
        """
        Parse cookie from cookie_path

        :param cookie_path: path of cookie file
        :type cookie_path: str
        :return: string cookie
        :rtype: str
        """
        if os.path.exists(cookie_path):
            if os.path.isfile(cookie_path):
                with open(cookie_path, 'r') as f:
                    cookie_text = f.read()
                    try:
                        json_result = CheggScraper.parse_json(cookie_text)
                        logging.debug(f'::cookie_path: {cookie_path} is json file')
                        return CheggScraper.dict_to_cookie_str(json_result).strip()
                    except JsonParseError:
                        logging.debug(f'::cookie_path: {cookie_path} is not json file')
                        return cookie_text.strip()
            else:
                logging.error(msg=f"{cookie_path} is not a file")
        else:
            logging.error(msg=f"{cookie_path} don't exist")
        raise CookieFileDoesNotExist(cookie_path)

    @staticmethod
    def clean_url(url: str) -> Tuple[bool, Optional[int], str]:
        """
        Cleans the url, So no track id goes to url
        """
        # https://www.chegg.com/homework-help/questions-and-answers/question--choose-random-questions-answer-possible-least-5-questions--thank-q8125333
        chapter_type = False
        q_id = None
        match = re.search(r'chegg\.com/homework-help/questions-and-answers/([^ ?/\n]+)-q(\d+)', url)
        if not match:
            chapter_type = True
            match = re.search(r'chegg\.com/homework-help/[^?/]+', url)
            if not match:
                logging.error(f'THIS URL NOT SUPPORTED\nurl: {url}')
                raise UrlNotSupported(url)
        else:
            q_id = int(match.group(2))

        return chapter_type, q_id, 'https://www.' + match.group(0)

    @staticmethod
    def final_touch(html_text: str) -> str:
        """
        Final changes to final html code, like changing class of some divs
        """
        soup = BeautifulSoup(html_text, 'html.parser')
        #print(soup)
        if soup.find('div', {'id': 'show-more'}):
            soup.find('div', {'id': 'show-more'}).decompose()
        if soup.find('section', {'id': 'general-guidance'}):
            soup.find('section', {'id': 'general-guidance'})['class'] = 'viewable visible'

        return str(soup)

    def _web_response(self, url: str, headers: dict = None, extra_headers: dict = None, expected_status: tuple = (200,),
                      note: str = None, error_note: str = "Error in request", post: bool = False, data: dict = None,
                      _json=None, raise_exception=False) -> Response:
        """
        Returns response from web
        """

        if not headers:
            headers = self.headers
        if extra_headers:
            headers.update(extra_headers)
        if post:
            response = requests.post(
                url=url,
                headers=headers,
                json=_json,
                data=data
            )
        else:
            response = requests.get(
                url=url,
                headers=headers)

        if response.status_code not in expected_status:
            logging.error(msg=f'Expected status codes {expected_status} but got {response.status_code}\n{error_note}')
            if raise_exception:
                raise UnexpectedStatusCode(response.status_code)
            return response
        if note:
            logging.info(msg=note)
        return response

    def _get_response_text(self, url: str, headers: dict = None, extra_headers: dict = None,
                           expected_status: tuple = (200,), note: str = None,
                           error_note: str = "Error in request", raise_exception=False) -> str:
        """
        text response from web

        :return: Text response from web
        :rtype: str
        """
        logging.debug(msg=f'::getting response from url: {url}')
        response = self._web_response(url=url, headers=headers, extra_headers=extra_headers,
                                      expected_status=expected_status, note=note,
                                      error_note=error_note, raise_exception=raise_exception)
        logging.info(msg=f'::response status code: {response.status_code}')
        if response.status_code not in expected_status:
            raise Exception(f'Expected status code {expected_status} but got {response.status_code}\n{error_note}')
        return response.text

    def _get_response_dict(self, url: str, headers: dict = None, extra_headers: dict = None,
                           expected_status: tuple = (200,), note: str = None, error_note: str = "Error in request",
                           post: bool = False, data: dict = None, _json=None, raise_exception=False) -> dict:
        """
        dict response from web

        :return: json response from web
        :rtype: dict
        """
        logging.info(msg=f'::getting response from url: {url}')
        response = self._web_response(url=url, headers=headers, extra_headers=extra_headers,
                                      expected_status=expected_status, note=note, error_note=error_note, post=post,
                                      data=data, _json=_json, raise_exception=raise_exception)
        logging.info(msg=f'::response status code: {response.status_code}')
        logging.debug(msg=f'::response text: {response.text}')
        return self.parse_json(response.text)

    @staticmethod
    def _parse_heading(soup: BeautifulSoup) -> str:
        """
        Parse heading from html

        @param soup: BeautifulSoup from chegg_html
        @type soup: BeautifulSoup
        @return: heading of the question page
        @rtype: str
        """
        heading = None
        heading_data = soup.find('script', id='__NEXT_DATA__')
        if heading_data:
            heading_data = heading_data.text
            #print(f"\n\nheading_data: {heading_data}\n\n")
            try:
                heading = json.loads(heading_data)['query']['qnaSlug']
            except:
                heading = json.loads(heading_data)['query']['hwhSlug']
                pass
        if not heading:
            title = soup.find('title')
            if title:
                heading = title.text

        if not heading:
            logging.error(msg="can't able to get heading")
        else:
            logging.info(msg=f"Heading: {heading}")
        return str(heading)

    def _get_non_chapter_type_data(self, legacy_id: int, auth_token: str) -> dict:
        """
        Get non chapter type quetion and answer data from chegg api
        """
        logging.info(msg="Getting non chapter type data, legacy_id: {}".format(legacy_id))

        query = {
            "operationName": "QnaPageQuestionByLegacyId",
            "variables": {
                "id": legacy_id
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "26efed323ef07d1759f67adadd2832ac85d7046b7eca681fe224d7824bab0928"
                }
            }
        }
        graphql_url = 'https://gateway.chegg.com/one-graph/graphql'

        extra_headers = {
            'authorization': f'Basic {auth_token}',
            'content-type': 'application/json',
            'apollographql-client-name': 'chegg-web',
            'apollographql-client-version': 'main-127d14c8-2503803178'
        }

        data = self._get_response_dict(url=graphql_url, post=True, _json=query, extra_headers=extra_headers)
        try: 
            if data['errors']:
                logging.error(msg=f"Error in getting non chapter type data, legacy_id: {legacy_id}")
                logging.error(msg=f"Error: {data['errors']['message']}")
                if (restrictions := data['errors']['message'].get('extensions', {}).get('metadata', {}).get(
                        'accessRestrictions')) and 'DEVICE_ALLOWED_QUOTA_EXCEEDED' in restrictions:
                    raise DeviceAllowedQuotaExceeded
        except KeyError:
            # No errors found
            pass
        
        #print(f"DATA: {data}")
        return data

    def _get_chapter_type_data(self, token: str, html_text: str) -> dict:
        isbn13 = str(re.search(r'"isbn13":"(\d+)"', html_text).group(1))
        problemId = str(re.search(r'"problemId":"(\d+)"', html_text).group(1))

        json_data = {
            'operationName': 'SolutionContent',
            'variables': {
                'ean': isbn13,
                'problemId': problemId,
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': '0322a443504ba5d0db5e19b8d61c620d5cab59c99f91368c74dcffdbea3e502f',
                },
            },
        }
        graphql_url = 'https://gateway.chegg.com/one-graph/graphql'
        cookies = {
    '_pxvid': 'bd2b85fe-a593-11ed-8f96-556b51777a46',
    '_cs_c': '0',
    '_ga': 'GA1.2.1776477376.1675646965',
    '_fbp': 'fb.1.1675646972280.820576136',
    '_tt_enable_cookie': '1',
    '_ttp': 'DN5xpqMFKJkOJLPXI8OOnbLsXxa',
    'optimizelyEndUserId': 'oeu1675823620851r0.8304850818441125',
    'C': '0',
    'O': '0',
    'exp': 'C026A',
    'expkey': '13417965AB0A666C8ED576A64210E72D',
    'forterToken': 'b23f4d54cf084d1fb9719f6a8a8b1791_1675823626666__UDF43_13ck',
    '__gads': 'ID=616e99e4b51fa258:T=1675823632:S=ALNI_MYowAAbsTlnNEyfsF2Jpnc3AXgjmA',
    '_gcl_au': '1.1.389950071.1675646966.2138176320.1675823637.1675823746',
    'refresh_token': 'ext.a0.t00.v1.MSjgXTecsWC71-aj7IEDMwFjtgg1a9YNHqU33f-ym7xOk0D4_UduY0Dm2uWq8I_BGwruibHrN1q5KQxeMc5IAIw',
    'id_token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IkNoZWdnYWxsZmFjQGdtYWlsLmNvbSIsImlzcyI6Imh1Yi5jaGVnZy5jb20iLCJzdWIiOiJhY2UyYzEyZi0zMmEyLTQxN2MtODgzOC0xNzY1YmUyOThiZjYiLCJhdWQiOiJDSEdHIiwiaWF0IjoxNjc1ODIzNzUwLCJleHAiOjE2OTEzNzU3NTAsInJlcGFja2VyX2lkIjoiYXB3In0.wa7XttAEfwBaXuGyf5p6qbcxX98VXsc-ZdRbvIi_5vTGowFyGXOUDGw995e7rafCzTaHBIw6hIRWOnMn7wV6j_hadtKwCXNH0YpdhtuBgGNeOEcYUBzlrYBFwpbbgxEUOLgQ0kcAaV6MSAmJ6oW2wnVrT6VrKDrfr22kQUnU4bqyzeRMU2uPlWCroB_5vVbVR0CIeIogQOAuZZ4PCEUZua3PjxfeB_L-1jnFNRSNQjOLjvYliP7WGtArMOjDtwRP2gWNA0OYlq4WYvTzCtw6zTdD9xQcRcJGOsguViw4532A0XPw9cd1V0TMNwLnuTU3FxcWZU8EPdq_N0ObLHHM1w',
    'U': '342267c90c025ff81dc25847dd832d46',
    '_pubcid': 'fbcd7572-8990-4725-85f2-286a5a6a9122',
    '_iidt': 'n/5Kzfn0rvXdJqze/vpeQHlacV6VCmetWKdrBxfcpKdWUTHWVJyGIWdxz/bkqEZxgXUwksGjLtv4pq2DmdtPquv9jw==',
    '_vid_t': '72wwiePvtbpIjIdF43M54//CEsDsYrKD5OSbURLHARa5gMu3burxzTpiZR4SbNwC2i9HWWZsNP86S1I8eIobw1N/3w==',
    'DFID': 'web|0n66QXMTVw6MKJyZh5SC',
    '_scid': 'f5ae9712-c5f9-4172-b41b-a155cc381365',
    '_sctr': '1|1675746000000',
    'V': '9ae2236d1860842bdcaf3f070af444d063e5b59ba45a1c.32685354',
    '_gid': 'GA1.2.1134296694.1675998624',
    'opt-user-profile': 'ace2c12f-32a2-417c-8838-1765be298bf6%252C22383174742%253A22473560126%252C22027151712%253A22030841005%252C22676901331%253A22719991359%252C21582730015%253A21585790242%252C22578180392%253A22595130475%252C23015360008%253A23003820007%252C22806995500%253A22814540677%252C21745990891%253A21741661939',
    'CVID': 'edb7f79f-707d-42c8-88ee-aaf560c5c628',
    '_cs_id': '76f352e0-0f34-a08a-9648-7bc3e43423cc.1675646981.11.1676044337.1676044337.1.1709810981919',
    '_awl': '2.1676044375.5-87aa1b3c6a4d970df015798f55dee345-6763652d75732d6561737431-0',
    'country_code': 'US',
    'user_geo_location': '%7B%22country_iso_code%22%3A%22US%22%2C%22country_name%22%3A%22United+States%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-US%22%5D%7D%7D',
    'PHPSESSID': '154iebcs7utpcioeritij1uvvk',
    'CSessionID': '68778fa5-c86c-40e0-9fa7-6487dcfef254',
    'SU': 'pkdIh1CwBRUQtYHmHWckO3-O7MEy0MwfW7f2yjCO-gnByEXU28D4vV2fgLTkOgNpTzX9pbzDlRNmQHPu0K7nIcdCKeR8Wnb7utxU4SFqDieVSRegfCbnHQT6RED-eBX4',
    'pxcts': 'a089a22a-a966-11ed-9768-537367444b65',
    'local_fallback_mcid': '84219933146126523994541375058474523054',
    's_ecid': 'MCMID|84219933146126523994541375058474523054',
    'IR_gbd': 'chegg.com',
    '__gpi': 'UID=000009eb2f592123:T=1675823632:RT=1676060630:S=ALNI_MY1hFnJMaqaE4Mg3fjGh9YHYYtpXQ',
    'CSID': '1676072970932',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Fri+Feb+10+2023+20%3A51%3A21+GMT-0500+(hora+de+Ecuador)&version=6.39.0&isIABGlobal=false&hosts=&consentId=23fba12a-83bb-4e10-a396-5d4e863f5a8f&interactionCount=1&landingPath=NotLandingPage&groups=fnc%3A1%2Csnc%3A1%2Ctrg%3A1%2Cprf%3A1&AwaitingReconsent=false',
    'IR_14422': '1676080299630%7C0%7C1676080299630%7C%7C',
    'ab.storage.deviceId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%22dd83a986-8912-8ba2-842c-93a1824269c8%22%2C%22c%22%3A1675823754068%2C%22l%22%3A1676080301923%7D',
    'ab.storage.userId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%22ace2c12f-32a2-417c-8838-1765be298bf6%22%2C%22c%22%3A1675823754056%2C%22l%22%3A1676080301925%7D',
    'ab.storage.sessionId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1': '%7B%22g%22%3A%222bf08ecf-38d7-72c4-c6c7-c7ab114a21de%22%2C%22e%22%3A1676082102003%2C%22c%22%3A1676080301920%2C%22l%22%3A1676080302003%7D',
    '_uetsid': '75e57350a8f011ed8102f58dc14e1d4a',
    '_uetvid': 'b21bc910a5bd11edac6b4decbe79578c',
    '_px3': '326b14ac08d140bc9601a3157bd56bdddbec3d5be13caead50e7d81ff705eeb7:UZR+yp51lugc814u9A2PkpACIDb2veE+XfI6MyjVRApap1Cb5PXzfcqqQsLIppVBAMYQpgOjLeRAWxKvehzqug==:1000:NyKW9qSAFEbPhD/UDP6jGmu9ef6PcKGl2go9Zss/c8llQiwR4AbdcNe6BIYLVAPyYBP5k/YUTA9FVGuMjxqQhH3HoVngYtfP2spvi3Wx3o+7ZoSZGe5t25wfxB42BySLnT6H3/UG0TsS5EOpbi1Ok/LQxr6lAzphA+uSGxzSK0uP+cHUQHLpaOfrvJtRul/wSMHabOU0q400u0pfQNftHg==',
    '_px': 'UZR+yp51lugc814u9A2PkpACIDb2veE+XfI6MyjVRApap1Cb5PXzfcqqQsLIppVBAMYQpgOjLeRAWxKvehzqug==:1000:5UHxMyXoEVkqKC3bITlqhQB0Dzc5Ti8o25J+9sC8OBTW0iiK27ihXkbw2uMU0GxxPHI7vTind7eOwchYbUkIidl0+CWJT23k22qzWK3HzIBEByyyZLB/UPl5R6q8pku7MAWOUvhSbEGBMEnW550X+07mfYJ8jVYL+SZ9ktB6qZrpwOdgyKmJxTrpta1IqCx2V19wDtVZ+Agt8Kw3XS5BfSty9E4zqiX46U6kPgmQ09aGJuQePYEarEAv7/aztRmSUUczH7dH5nlBRHNTnj3/Vw==',
}

        headers = {
    'authority': 'gateway.chegg.com',
    'accept': '*/*',
    'accept-language': 'es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5',
    'apollographql-client-name': 'chegg-web',
    'apollographql-client-version': 'main-2e838a9f-3753980649',
    'authorization': 'Basic TnNZS3dJMGxMdVhBQWQwenFTMHFlak5UVXAwb1l1WDY6R09JZVdFRnVvNndRRFZ4Ug==',
    'content-type': 'application/json',
    # 'cookie': '_pxvid=bd2b85fe-a593-11ed-8f96-556b51777a46; _cs_c=0; _ga=GA1.2.1776477376.1675646965; _fbp=fb.1.1675646972280.820576136; _tt_enable_cookie=1; _ttp=DN5xpqMFKJkOJLPXI8OOnbLsXxa; optimizelyEndUserId=oeu1675823620851r0.8304850818441125; C=0; O=0; exp=C026A; expkey=13417965AB0A666C8ED576A64210E72D; forterToken=b23f4d54cf084d1fb9719f6a8a8b1791_1675823626666__UDF43_13ck; __gads=ID=616e99e4b51fa258:T=1675823632:S=ALNI_MYowAAbsTlnNEyfsF2Jpnc3AXgjmA; _gcl_au=1.1.389950071.1675646966.2138176320.1675823637.1675823746; refresh_token=ext.a0.t00.v1.MSjgXTecsWC71-aj7IEDMwFjtgg1a9YNHqU33f-ym7xOk0D4_UduY0Dm2uWq8I_BGwruibHrN1q5KQxeMc5IAIw; id_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IkNoZWdnYWxsZmFjQGdtYWlsLmNvbSIsImlzcyI6Imh1Yi5jaGVnZy5jb20iLCJzdWIiOiJhY2UyYzEyZi0zMmEyLTQxN2MtODgzOC0xNzY1YmUyOThiZjYiLCJhdWQiOiJDSEdHIiwiaWF0IjoxNjc1ODIzNzUwLCJleHAiOjE2OTEzNzU3NTAsInJlcGFja2VyX2lkIjoiYXB3In0.wa7XttAEfwBaXuGyf5p6qbcxX98VXsc-ZdRbvIi_5vTGowFyGXOUDGw995e7rafCzTaHBIw6hIRWOnMn7wV6j_hadtKwCXNH0YpdhtuBgGNeOEcYUBzlrYBFwpbbgxEUOLgQ0kcAaV6MSAmJ6oW2wnVrT6VrKDrfr22kQUnU4bqyzeRMU2uPlWCroB_5vVbVR0CIeIogQOAuZZ4PCEUZua3PjxfeB_L-1jnFNRSNQjOLjvYliP7WGtArMOjDtwRP2gWNA0OYlq4WYvTzCtw6zTdD9xQcRcJGOsguViw4532A0XPw9cd1V0TMNwLnuTU3FxcWZU8EPdq_N0ObLHHM1w; U=342267c90c025ff81dc25847dd832d46; _pubcid=fbcd7572-8990-4725-85f2-286a5a6a9122; _iidt=n/5Kzfn0rvXdJqze/vpeQHlacV6VCmetWKdrBxfcpKdWUTHWVJyGIWdxz/bkqEZxgXUwksGjLtv4pq2DmdtPquv9jw==; _vid_t=72wwiePvtbpIjIdF43M54//CEsDsYrKD5OSbURLHARa5gMu3burxzTpiZR4SbNwC2i9HWWZsNP86S1I8eIobw1N/3w==; DFID=web|0n66QXMTVw6MKJyZh5SC; _scid=f5ae9712-c5f9-4172-b41b-a155cc381365; _sctr=1|1675746000000; V=9ae2236d1860842bdcaf3f070af444d063e5b59ba45a1c.32685354; _gid=GA1.2.1134296694.1675998624; opt-user-profile=ace2c12f-32a2-417c-8838-1765be298bf6%252C22383174742%253A22473560126%252C22027151712%253A22030841005%252C22676901331%253A22719991359%252C21582730015%253A21585790242%252C22578180392%253A22595130475%252C23015360008%253A23003820007%252C22806995500%253A22814540677%252C21745990891%253A21741661939; CVID=edb7f79f-707d-42c8-88ee-aaf560c5c628; _cs_id=76f352e0-0f34-a08a-9648-7bc3e43423cc.1675646981.11.1676044337.1676044337.1.1709810981919; _awl=2.1676044375.5-87aa1b3c6a4d970df015798f55dee345-6763652d75732d6561737431-0; country_code=US; user_geo_location=%7B%22country_iso_code%22%3A%22US%22%2C%22country_name%22%3A%22United+States%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-US%22%5D%7D%7D; PHPSESSID=154iebcs7utpcioeritij1uvvk; CSessionID=68778fa5-c86c-40e0-9fa7-6487dcfef254; SU=pkdIh1CwBRUQtYHmHWckO3-O7MEy0MwfW7f2yjCO-gnByEXU28D4vV2fgLTkOgNpTzX9pbzDlRNmQHPu0K7nIcdCKeR8Wnb7utxU4SFqDieVSRegfCbnHQT6RED-eBX4; pxcts=a089a22a-a966-11ed-9768-537367444b65; local_fallback_mcid=84219933146126523994541375058474523054; s_ecid=MCMID|84219933146126523994541375058474523054; IR_gbd=chegg.com; __gpi=UID=000009eb2f592123:T=1675823632:RT=1676060630:S=ALNI_MY1hFnJMaqaE4Mg3fjGh9YHYYtpXQ; CSID=1676072970932; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Feb+10+2023+20%3A51%3A21+GMT-0500+(hora+de+Ecuador)&version=6.39.0&isIABGlobal=false&hosts=&consentId=23fba12a-83bb-4e10-a396-5d4e863f5a8f&interactionCount=1&landingPath=NotLandingPage&groups=fnc%3A1%2Csnc%3A1%2Ctrg%3A1%2Cprf%3A1&AwaitingReconsent=false; IR_14422=1676080299630%7C0%7C1676080299630%7C%7C; ab.storage.deviceId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%22dd83a986-8912-8ba2-842c-93a1824269c8%22%2C%22c%22%3A1675823754068%2C%22l%22%3A1676080301923%7D; ab.storage.userId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%22ace2c12f-32a2-417c-8838-1765be298bf6%22%2C%22c%22%3A1675823754056%2C%22l%22%3A1676080301925%7D; ab.storage.sessionId.b283d3f6-78a7-451c-8b93-d98cdb32f9f1=%7B%22g%22%3A%222bf08ecf-38d7-72c4-c6c7-c7ab114a21de%22%2C%22e%22%3A1676082102003%2C%22c%22%3A1676080301920%2C%22l%22%3A1676080302003%7D; _uetsid=75e57350a8f011ed8102f58dc14e1d4a; _uetvid=b21bc910a5bd11edac6b4decbe79578c; _px3=326b14ac08d140bc9601a3157bd56bdddbec3d5be13caead50e7d81ff705eeb7:UZR+yp51lugc814u9A2PkpACIDb2veE+XfI6MyjVRApap1Cb5PXzfcqqQsLIppVBAMYQpgOjLeRAWxKvehzqug==:1000:NyKW9qSAFEbPhD/UDP6jGmu9ef6PcKGl2go9Zss/c8llQiwR4AbdcNe6BIYLVAPyYBP5k/YUTA9FVGuMjxqQhH3HoVngYtfP2spvi3Wx3o+7ZoSZGe5t25wfxB42BySLnT6H3/UG0TsS5EOpbi1Ok/LQxr6lAzphA+uSGxzSK0uP+cHUQHLpaOfrvJtRul/wSMHabOU0q400u0pfQNftHg==; _px=UZR+yp51lugc814u9A2PkpACIDb2veE+XfI6MyjVRApap1Cb5PXzfcqqQsLIppVBAMYQpgOjLeRAWxKvehzqug==:1000:5UHxMyXoEVkqKC3bITlqhQB0Dzc5Ti8o25J+9sC8OBTW0iiK27ihXkbw2uMU0GxxPHI7vTind7eOwchYbUkIidl0+CWJT23k22qzWK3HzIBEByyyZLB/UPl5R6q8pku7MAWOUvhSbEGBMEnW550X+07mfYJ8jVYL+SZ9ktB6qZrpwOdgyKmJxTrpta1IqCx2V19wDtVZ+Agt8Kw3XS5BfSty9E4zqiX46U6kPgmQ09aGJuQePYEarEAv7/aztRmSUUczH7dH5nlBRHNTnj3/Vw==',
    'origin': 'https://www.chegg.com',
    'referer': 'https://www.chegg.com/',
    'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78',
    'x-chegg-page-type': 'tbs-page',
    'x-chegg-referrer': 'homework-help/elementary-linear-algebra-11th-edition-chapter-5-problem-6se-solution-9781118473504?recommendationId=0b59b469-32e0-445c-9b54-8d50e75c8900&regionName=recent+activity&sectionId=c44dc0da-6a57-41d9-bdf6-3a3e8c25bbe7',
}


        #res_data = self._get_response_dict(url=graphql_url, post=True, _json=json_data)
        res_data = requests.post(f'{graphql_url}', cookies=cookies, headers=headers, json=json_data)
        #print(res_data)
        #print(json.dumps(res_data.json(), indent=2))
        return res_data

    def _parse_question_answer(self, legacy_id: Optional[int], html_text: str, chapter_type: bool, token: Optional[str],
                               auth_token: str):
        """
        Parse Question and Answers
        """
        if not chapter_type:
            data = self._get_non_chapter_type_data(legacy_id=legacy_id, auth_token=auth_token)
            question_div = data['data']['questionByLegacyId']['content']['body']
            #print(f"question_div: {question_div}")            
            answer_divs = [f"<div class=\"answer-given-body ugc-base\">{answers_['answerData']['html']}</div>" for
                           answers_ in
                           data['data']['questionByLegacyId']['htmlAnswers']]
            if answer_divs == []:
                print("Esta vacio")
                matches = re.findall(r'<html>(.*?)</html>', str(data))
                answer_divs = ''
                for match in matches:
                    answer_divs += f"<html>{match}</html>"
                pass
            else:
                print("Tiene Datos")
                pass
            #print(f"answer_divs: {answer_divs}")
            return question_div, '<ul class="answers-list">' + "".join(answer_divs) + "</ul>"
        else:
            return '<div></div>', self.render_chapter_type_html(
                self._get_chapter_type_data(token=token, html_text=html_text)
            )

    def _parse(self, html_text: str, token: Optional[str], q_id: Optional[int], auth_token: str,
               chapter_type: bool = None) -> Tuple[str, str, str, str]:
        html_text = self.replace_src_links(html_text)
        soup = BeautifulSoup(html_text, 'html.parser')
        logging.debug("HTML\n\n" + html_text + "HTML\n\n")

        if soup.find('div', id='px-captcha'):
            raise BotFlagError

        """Parse headers"""
        headers = soup.find('head')

        """Parse heading"""
        heading = self._parse_heading(soup)

        """Parse Question"""
        if not chapter_type:
            if not q_id:
                raise UnableToGetLegacyQuestionID

        question_div, answers_div = self._parse_question_answer(
            legacy_id=q_id, html_text=html_text, chapter_type=chapter_type, token=token, auth_token=auth_token
        )

        return str(headers), heading, self.replace_src_links(question_div), self.replace_src_links(answers_div)

    def _save_html_file(self, rendered_html: str, heading: str = None, question_uuid: str = None,
                        file_name_format: str = None):
        heading = self.slugify(heading.strip('.').strip())
        if not file_name_format:
            file_name_format = self.save_file_format
        if not file_name_format:
            file_name_format = heading + '.html'

        file_path = os.path.join(
            self.base_path,
            file_name_format)

        file_path = file_path.format(**{
            'random_u_str_int': ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
            'random_u_str': ''.join(random.choices(string.ascii_uppercase, k=10)),
            'random_str': ''.join(random.choices(string.ascii_letters, k=10)),
            'random_int': ''.join(random.choices(string.digits, k=10)),
            'heading': heading,
            'title': heading,
            'question_uuid': question_uuid
        })

        # if self.save_file_format:
        #     file_path = os.path.join(
        #         file_path,
        #         self.save_file_format)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        return file_path

    def _render_html(self, url, headers, heading, question_div, answers__):
        html_rendered_text = main_template.render(
            url=url,
            headers=headers,
            title=heading,
            heading=heading,
            question_body=question_div,
            answers_wrap=answers__,
            extra_header_tag=self.extra_header_tag,
        )

        return self.final_touch(html_text=html_rendered_text)

    def url_to_html(self, url: str, file_name_format: str = None, get_dict_info: bool = False):
        """
        Chegg url to html file, saves the file and return file path

        @param url: chegg url
        @type url: str
        @param get_dict_info:
        @type get_dict_info:
        @param file_name_format: File path to save file
        @type file_name_format: str
        @return: file_path
        @rtype:
        """
        chapter_type, q_id, url = self.clean_url(url)

        html_res_text = self._get_response_text(url=url)
        try:
            token = re.search(r'"token":"(.+?)"', html_res_text).group(1)
        except AttributeError:
            token = None
        #if chapter_type and not token:
        #    raise UnableToGetToken

        # static
        auth_token = "TnNZS3dJMGxMdVhBQWQwenFTMHFlak5UVXAwb1l1WDY6R09JZVdFRnVvNndRRFZ4Ug=="

        headers, heading, question_div, answers__ = self._parse(
            html_text=html_res_text,
            q_id=q_id,
            chapter_type=chapter_type,
            token=token,
            auth_token=auth_token
        )

        rendered_html = self._render_html(url, headers, heading, question_div, answers__)

        file_path = self._save_html_file(rendered_html, heading, None, file_name_format)

        if get_dict_info:
            return file_path, url, headers, heading, question_div, answers__
        return file_path
