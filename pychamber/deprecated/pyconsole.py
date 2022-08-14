import pyqtconsole.highlighter as hl
from pyqtconsole.console import PythonConsole

themes = {
    'nightowl-light': {
        'bg': '#fbfbfb',
        'fg': '#403f53',
        'colors': {
            'keyword': hl.format('#994cc3', 'bold'),
            'operator': hl.format('#0c969b'),
            'brace': hl.format('#403f53'),
            'defclass': hl.format('#111111', 'bold'),
            'string': hl.format('#c96765'),
            'string2': hl.format('#c96765'),
            'comment': hl.format('#989fb1', 'italic'),
            'self': hl.format('#aa0982'),
            'numbers': hl.format('#aa0982'),
            'inprompt': hl.format('#0C969B', 'bold'),
            'outprompt': hl.format('#0C969B', 'bold'),
        },
    },
    'moonlight-ii': {
        'bg': '#222436',
        'fg': '#c8d3f5',
        'colors': {
            'keyword': hl.format('#c099ff', 'bold'),
            'operator': hl.format('#86e1fc'),
            'brace': hl.format('#ffc777'),
            'defclass': hl.format('#ffc777', 'bold'),
            'string': hl.format('#c3e88d'),
            'string2': hl.format('#c3e88d'),
            'comment': hl.format('#191a2a', 'italic'),
            'self': hl.format('#fc7b7b'),
            'numbers': hl.format('#ff966c'),
            'inprompt': hl.format('#7f85a3', 'bold'),
            'outprompt': hl.format('#7f85a3', 'bold'),
        },
    },
}


class PyConsole(PythonConsole):
    def __init__(self, theme: str, parent=None, locals=None, formats=None) -> None:
        colors = themes[theme]['colors']
        super().__init__(parent=parent, locals=locals, formats=colors)
        self.setStyleSheet(
            f'color: {themes[theme]["fg"]}; background-color: {themes[theme]["bg"]}'
        )
