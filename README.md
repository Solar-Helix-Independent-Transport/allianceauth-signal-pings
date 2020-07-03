# Signal Pings

This is a simple plugin for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) to send a "signal" to a discord webhook when a user does something in auth.

## Current Signals

- Group Join / Group Leave
- HR applications
- Timers and Fleets

## TODO/Wishlist

- Some translations

## Setup

1. `pip install allianceauth-signal-pings`
2. add `'signalpings',` to INSTALLED_APPS in your local.py
3. migrate database and restart auth
4. Setup your webhooks in the admin panel 
5. setup groups to ping in the admin panel
6. prepare for pingagedon.

## Pics 

### Admin Create Webhooks
![Imgur](https://i.imgur.com/CgoA7za.png)

### Admin create groups to signal
![Imgur](https://i.imgur.com/R7Fb7S9.png)

###  Pings
![Imgur](https://i.imgur.com/UfojsOk.png)

## Contribute

All contributions are welcome, but please if you create a PR for functionality or bugfix, do not mix in unrelated formatting changes along with it.
