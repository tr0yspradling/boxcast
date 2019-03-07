==================
boxcast-python-sdk
==================

Unofficial BoxCast SDK for Python.

Requirements
------------
* `Requests <http://docs.python-requests.org/en/master/>`_

Features
--------
* Return playlist views with broadcasts (.m3u8 / .mp4).
* Only GET requests work at the moment.
* Update & delete methods coming soon.


Example:
::
  from boxcast import BoxCastClient

  client = BoxCastClient('client_id', 'client_secret', 'email', 'password')

  account = client.get_account()
  boxcasters = client.get_boxcasters()
  channels = client.get_channels()
  broadcasts = client.get_broadcasts()

  print('Account: %s' % account.name)

  for _boxcaster in boxcasters:
      print('BoxCaster: %s' % _boxcaster.id)

  for _broadcast in broadcasts:
      print('Broadcast: %s' % _broadcast.name)

  for _channel in channels:
      print('Channel: %s' % _channel.name)

  channel_broadcasts = client.get_channel_broadcasts(channels[0].id)

Output (redacted):
::
  Account: ************
  BoxCaster: ************
  BoxCaster: ************
  Broadcast: ReDiscover Louisa s02e21
  Broadcast: "The Big Picture" S1:E1
  Broadcast: Live Boyd County Boys Basketball Vs. Pikeville
  Broadcast: ACCM 12.14.2007
  Broadcast: ACCM 09.28.2017
  Broadcast: ACCM 08.24.2017
  Broadcast: ACCM 10.26.2017
  Broadcast: S1:E15
  Broadcast: Mr. Basketball?
  Broadcast: S1:E16
  Broadcast: Boyd County Boys Basketball S18:E0213
  Broadcast: Growing In Lawrence County S1:E17
  Broadcast: ReDiscover Louisa S2:E20
  Broadcast: Growing in Lawrence County S1:E18
  Broadcast: ReDiscover Louisa S2:E21
  Broadcast: ReDiscover Louisa S2:E22
  Broadcast: First Round Coverage of the Girls 64th District Tournament
  Broadcast: First Round Boys 64th District Tournament
  Broadcast: Basketball - Boys 64th District First Round Ashland V Fairview
  Broadcast: Girls 64th District Championship Game
  Channel: 2018 16th Region Basketball Tournament
  Channel: 2018 Boys 64th District Tournament
  Channel: 2018 Girls 64th District Tournament
  Channel: Ashland City Commissioners Meetings
  Channel: Boyd County Boys Basketball 2017-18
  Channel: Boyd County Girls Basketball 2017-18
  Channel: Cross Section
  Channel: Growing in Lawrence County
  Channel: My Town TV Live
  Channel: The Big Picture


* Free software: MIT license
