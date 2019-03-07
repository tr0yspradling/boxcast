# -*- coding: utf-8 -*-

"""Top-level package for boxcast-python-sdk."""

__author__ = """Troy Spradling"""
__email__ = 'troy@slgmediagroup.com'
__version__ = '0.1.1'

import requests
import json
import base64
import logging
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class BoxCastClient(object):
    """ BoxCast API Client """

    # API Endpoints
    resource_endpoints = {
        'root': 'https://api.boxcast.com/',
        'account': 'https://api.boxcast.com/account',
        'channels': 'https://api.boxcast.com/account/channels',
        'channel_details': 'https://api.boxcast.com/account/channels/{id}',
        'channel_broadcasts': 'https://api.boxcast.com/channels/{id}/broadcasts',
        'broadcast_detail': 'https://api.boxcast.com/broadcasts/{id}',
        'broadcast_view': 'https://api.boxcast.com/broadcasts/{id}/view',
        'boxcasters': 'https://api.boxcast.com/boxcasters',
        'boxcaster_detail': 'https://api.boxcast.com/boxcasters/{id}'
    }

    oauth_endpoints = {
        'authorize': 'https://auth.boxcast.com/oauth2/authorize',
        'token': 'https://auth.boxcast.com/oauth2/token'
    }

    def __init__(self, client_id, client_secret, logger=None):
        self.access_token = None
        self.client_id = client_id
        self.client_secret = client_secret
        auth_str = ('%s:%s' % (self.client_id, self.client_secret)).encode()
        self.basic_auth_token = base64.b64encode(auth_str).decode('UTF-8')
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.authorize()

    @staticmethod
    def __auth_params():
        return {
            'params': {
                'grant_type': 'client_credentials',
                'scope': 'owner'
            }
        }

    @staticmethod
    def __auth_headers():
        return {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def __general_headers(self):
        return {
            'Authorization': 'Bearer %s' % self.access_token,
            'Content-Type': 'application/json'
        }

    @staticmethod
    def __prep_pagination_args(page_number=0, limit_size=50, sort_order=''):
        return '?p={0}&s={1}&l={2}'.format(page_number, sort_order, limit_size)

    def authorize(self):
        """ Authorize & retrieve access_token. """
        response = requests.post(url=self.oauth_endpoints['token'],
                                 headers=self.__auth_headers(),
                                 auth=(self.client_id, self.client_secret),
                                 data=self.__auth_params().get('params'))
        self.logger.info(response)
        if response.ok:
            logging.info('Authorization successful. Saving OAuth access_token.')
            self.access_token = response.json().get('access_token')
        else:
            # Add BoxCast info
            self.logger.error('Authorization request failed!')
            self.logger.error(response.json())
            raise Exception(response.json())

    def _get(self, endpoint, headers=None):
        """ Return a tuple of headers and JSON payload """
        if not headers:
            headers = {}
            headers.update(self.__general_headers())
        response = requests.get(endpoint, headers=headers)
        if response.content is not b'':
            self.logger.info(response)
            self.logger.info(response.json())
            return response.headers, response.json()

        self.logger.error('Request failed!')
        self.logger.error(response)
        self.logger.error(response.json())

    def get(self, endpoint):
        """ Returns JSON payload """
        return self._get(endpoint)[1]

    def get_paginated(self, endpoint):
        """ Blocking function. Returns a list of results. """
        results_list = []
        # _get returns (headers, json_body), so we have to use _get(x)[1]

        url = endpoint + self.__prep_pagination_args(sort_order='')
        response = self._get(url)
        for _result in response[1]:
            results_list.append(_result)
        pagination_header_json = json.loads(response[0]['X-Pagination'])
        while 'last' in pagination_header_json:
            next = pagination_header_json['next']
            url = endpoint + self.__prep_pagination_args(next, sort_order='')
            _response = self._get(url)
            for _result in _response[1]:
                results_list.append(_result)
            pagination_header_json = json.loads(_response[0]['X-Pagination'])
        return results_list

    def get_account(self):
        """ Returns all fields for the current account. """
        response = self.get(self.resource_endpoints['account'])
        return Account(**response)

    def get_boxcasters(self):
        """ Returns summary fields for all BoxCasters on the current account. """
        response = self.get(self.resource_endpoints['boxcasters'])
        return [BoxCaster(**_boxcaster) for _boxcaster in response]

    def get_boxcaster_detail(self, id):
        """ Returns all fields for the specified BoxCaster. """
        endpoint = self.resource_endpoints['boxcaster_details'].format(id=id)
        boxcaster = BoxCaster(**self.get(endpoint))
        boxcaster.live = True if boxcaster.status == 'broadcasting' else False
        return boxcaster

    def get_boxcaster_channel(self, id):
        """ Returns the auto-created channel for a specific BoxCaster """
        channel_id = self.get_boxcaster_detail(id).channel_id
        return self.get_channel_detail(channel_id)

    def update_boxcaster(self, id, name):
        """ Updates the supplied fields of the specified BoxCaster. """
        # endpoint = self.resource_endpoints['boxcaster_detail'].format(id=id)
        # data = {'name': name}
        # response = requests.put(endpoint, json=json.dumps(data))
        # return response
        pass

    def get_current_or_upcoming_broadcasts(self):
        channel_id = self.get_account().channel_id
        endpoint = self.resource_endpoints['channel_broadcasts'].format(id=channel_id) + '?q=timeframe:current%20timeframe:future'
        result_list = self.get(endpoint)
        broadcast_list = []
        for _broadcast in result_list:
            broadcast = Broadcast(**_broadcast)
            broadcast.view = self.get_broadcast_view(broadcast.id)
            broadcast_list.append(broadcast)
        return broadcast_list

    def get_channels(self):
        """ Returns summary fields for all channels on the current account. """
        result_list = self.get_paginated(self.resource_endpoints['channels'])
        return [Channel(**_result) for _result in result_list]

    def get_channel_detail(self, id):
        """ Returns all fields for the specified channel. """
        endpoint = self.resource_endpoints['channel_details'].format(id=id)
        return Channel(**self.get(endpoint))

    def get_channel_boxcaster(self, id):
        """ Returns all fields of the BoxCaster associated with the specified channel """
        boxcaster_id = self.get_channel_detail(id).boxcaster_id
        return self.get_boxcaster_detail(boxcaster_id)

    def update_channel(self, id):
        """ Updates the supplied fields of the specified channel. """
        pass

    def get_account_broadcasts(self):
        """
        Returns summary fields for all broadcasts on the current account.
        Please be aware that the results may be paginated.
        """
        channel_id = self.get_account().channel_id
        response = self.get_paginated(
            self.resource_endpoints['channel_broadcasts'].format(id=channel_id))
        return [Broadcast(**_broadcast) for _broadcast in response]

    def get_account_broadcasts_with_view(self):
        """
        Returns summary fields for all broadcasts on the current account, with
        the BroadcastView.
        Please be aware that the results may be paginated.
        """
        channel_id = self.get_account().channel_id
        return self.get_channel_broadcasts_with_view(channel_id)

    def get_channel_broadcasts(self, id):
        """ Returns minimal fields for all broadcasts in the specified channel. """
        endpoint = self.resource_endpoints['channel_broadcasts'].format(id=id)
        return [Broadcast(**broadcast) for broadcast in self.get_paginated(endpoint)]

    def get_channel_broadcasts_with_view(self, id):
        """ Returns minimal fields for all broadcasts in the specified channel with the view. """
        broadcasts = []
        for _broadcast in self.get_channel_broadcasts(id):
            _broadcast.view = self.get_broadcast_view(_broadcast.id)
            broadcasts.append(_broadcast)
        return broadcasts

    def get_broadcast_detail(self, id):
        """ Returns all fields for the specified broadcast. """
        endpoint = self.resource_endpoints['broadcast_detail'].format(id=id)
        return Broadcast(**self.get(endpoint))

    def get_broadcast_with_view(self, id):
        """ Returns all fields for the specified broadcast with the view. """
        broadcast_endpoint = self.resource_endpoints['broadcast_detail'].format(id=id)
        broadcast_view_endpoint = self.resource_endpoints['broadcast_view'].format(id=id)
        broadcast = Broadcast(**self.get(broadcast_endpoint))
        broadcast.view = BroadcastView(**self.get(broadcast_view_endpoint))
        return broadcast

    def get_broadcast_view(self, id):
        """ Returns a BroadcastView for the specifid broadcast. """
        view_endpoint = self.resource_endpoints['broadcast_view'].format(id=id)
        return BroadcastView(**self.get(view_endpoint))

    def schedule_broadcast(self, broadcast):
        """ Creates a new scheduled broadcast from the supplied fields. """
        pass

    def update_broadcast(self, id):
        """ Updates the supplied fields of the specified broadcast. """
        pass

    def delete_broadcast(self, id):
        """ Deletes a broadcast from the account. """
        pass


class BoxCastResource(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        if hasattr(self, 'id') and hasattr(self, 'name'):
            return '<{resource} ({id}) Name: {name}>'.format(
                   resource=self.__class__.__name__, id=self.id, name=self.name)
        else:
            return '<{resource}>'.format(resource=self.__class__.__name__)


class Account(BoxCastResource):
    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)


class BoxCaster(BoxCastResource):
    def __init__(self, **kwargs):
        super(BoxCaster, self).__init__(**kwargs)


class Broadcast(BoxCastResource):
    def __init__(self, **kwargs):
        super(Broadcast, self).__init__(**kwargs)


class BroadcastView(BoxCastResource):
    def __init__(self, **kwargs):
        super(BroadcastView, self).__init__(**kwargs)

    def is_hls(self):
        return True if '.m3u8' in self.playlist else False

    def get_sanitized_playlist_url(self):
        """ https://docs.python.org/3/library/urllib.parse.html#urllib.parse.unquote """
        if self.playlist:
            return unquote(self.playlist)
        else:
            return None


class Channel(BoxCastResource):
    def __init__(self, **kwargs):
        super(Channel, self).__init__(**kwargs)
