from flask import Markup

def alert(text, category="danger"):
    return Markup('<div class="alert alert-{}" role="alert">{}</div>'.format(category, text))