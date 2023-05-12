import configparser

config_name = 'config.ini'

def write_config(hotkey, delay, frequency, button):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {
        'hotkey_key': hotkey,
        'delay': str(delay),
        'frequency': str(frequency),
        'button': str(button)
    }

    with open(config_name, 'w') as config_file:
        config.write(config_file)


def load_config():
    config = configparser.ConfigParser()
    config.read(config_name)

    if 'SETTINGS' in config:
        settings = config['SETTINGS']
        hotkey_key = settings.get('hotkey_key', 'F6')
        delay = settings.getfloat('delay', 0.1)
        frequency = settings.getint('frequency', 10)
        button = settings.getint('button', 0)
        return hotkey_key, delay, frequency, button

    return 'F6', 0.1, 10, 0


hotkey = 'F6'
delay = 0.01
frequency = 10
button = 0

write_config(hotkey, delay, frequency, button)

# hotkey, delay, frequency = load_config()
#
# print(hotkey,delay,frequency)