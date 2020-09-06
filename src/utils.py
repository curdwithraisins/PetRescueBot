#!/usr/bin/env python3

import os

from dotenv import load_dotenv

def get_env(name):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    return os.getenv(name)