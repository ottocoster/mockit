# Device Imitator

`device_imitator` is a simple ssh server to respond to predefined commands. It was created to be used in integratation tests.

## Work in progress

There are still a lot of basic commands to add and more functionality

## Getting started

The previously retrieved command output needs to be stored in a directory, one per device. The file needs to be named as the exact command.

## Device version

For mikrotik we currently support multiple version. With `DEVICE_VERSION` you can switch between the two. We will probably add more version for devices in the future.

You can add your own folder to the config/<device> folder for your own version and use the folders name as the `DEVICE_VERSION`

## SSH Server

### Add a static command

You can add a static command response in `/config/<device>/templates`. The name of the file has to equal the command being executed

### Add a dynamic command

You can create a dynamic command response in `/config/<device>/scripts`. Whenever a command is called, it first goes thought the `def handle_command` in __init__.py. 
For a basic example see `/config/juniper_junos/scripts/__init__.py`.

## SNMP Server

### Info

SNMP currently only works for arista_eos, cisco_ios, cisco_nxos, juniper_junos, mikrotik. 
We are currently gathering information about what kind of responses different devices give.

## Docker compose

### Example

```yml
version: "3"
name: devices
services:
  cisco_ios:
    image: registry.gitlab.com/slurpit.io/device_imitator:latest
    container_name: cisco_ios
    environment:
      DEVICE_TYPE: cisco_ios
      SSH_USERNAME: test
      SSH_PASSWORD: test
    ports: 
      - "22:22"
      - "161:161/udp"
    volumes:
      - ./configs/cisco_ios:/configs/cisco_ios
```

### Info

To be able to add your own commands or scripts easily we make a columns of the configs/<device> folder.

To connect to the device remotely through ssh we open the 22 port and for snmp the 161/udp port.

# Development info

## githook
- `git config core.hooksPath .githooks` to automatically increment the version number


