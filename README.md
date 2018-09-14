# ralogs

ralogs is a simple python script which connects to Rancher and stream logs 
directly to your terminal from multiple containers within a single stack.

## Requirements

ralogs requires Python and pip to be installed on your machine. It has been tested only with Python 3.5.

## Changelog

1.1 
- Added third parameter to specify a service
- Added container names and IDs to the logs output

1.0 
- Initial release

## Installation

```
$ pip install ralogs
```

## Configuration

Check if installation was successful:
```
$ ralogs -v
```
It should display version info. Now open and edit configs:
```
$ subl $HOME/.ralogs
```

- rancher_url - where you can access Rancher (eg. https://rancher.example.com)
- api_key and api_secret - this you can create in Rancher GUI, go to API -> Keys from top menu and add new Account API Key 

## Usage:

```
$ ralogs environment stack
```

If the stack has more than one service, you can select it by name by adding third argument:

```
$ ralogs environment stack service
```