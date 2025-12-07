#!/bin/bash
pytest --color=yes -v --durations 0 -rP $pyci test_ssh_telnet.py
