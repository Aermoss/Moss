import moss, sdl2, sdl2.ext, sdl2.sdlmixer, os

class Mixer:
    def __init__(self):
        sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
        sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
        self.channels = []

    def load(self, file):
        moss.logger.log(moss.INFO, f"loaded audio file: \"{os.path.split(file)[1]}\".")
        return sdl2.sdlmixer.Mix_LoadWAV(file.encode())

    def play(self, sound, volume = 255, loop = 0):
        if len(self.channels) >= 8:
            sdl2.sdlmixer.Mix_HaltChannel(self.channels[0])
            self.channels.pop(0)

        queue = []

        for index, i in enumerate(self.channels):
            if not sdl2.sdlmixer.Mix_Playing(i):
                queue.append(index)

        for index, i in enumerate(queue):
            self.channels.pop(i - index)

        channel = sdl2.sdlmixer.Mix_PlayChannel(-1, sound, loop)
        sdl2.sdlmixer.Mix_Volume(channel, int(volume / 2))
        self.channels.append(channel)