import configparser

def write_config(hotkey, delay, frequency):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {
        'hotkey': hotkey,
        'delay': str(delay),
        'frequency': str(frequency)
    }

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if 'SETTINGS' in config:
        settings = config['SETTINGS']
        hotkey = settings.get('hotkey', '')
        delay = settings.getfloat('delay', 0.1)
        frequency = settings.getint('frequency', 5)

        return hotkey, delay, frequency

    return '', 0.1, 5


hotkey = 'F1'
delay = 0.1
frequency = 5

write_config(hotkey, delay, frequency)

# hotkey, delay, frequency = load_config()
#
# print(hotkey,delay,frequency)