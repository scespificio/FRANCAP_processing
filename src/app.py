import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import login as log
from menu import menu

import pandas as pd
import os, sys
import re
import io
import math
import numpy as np
from dotenv import load_dotenv
import warnings



st.set_page_config(layout="wide")

#log.login()
menu()
st.switch_page("pages/acquisition.py")





















































































































