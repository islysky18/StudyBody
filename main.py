import os
from dotenv import load_dotenv
import openai
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st

load_dotenv()

client = openai.OpenAI()

model = "gpt-4-1106-preview"
