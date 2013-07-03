def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))
