import pygame
from openai import OpenAI
import os
import time
from helpers import FastReadApp

# export OPENAI_API_KEY=
pygame.init()

app = FastReadApp()
app.run()

pygame.quit()
