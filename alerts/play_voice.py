import pygame

pygame.mixer.init()

def play_voice(file_path):

    try:

        pygame.mixer.music.load(file_path)

        pygame.mixer.music.play()

    except Exception as e:

        print(e)