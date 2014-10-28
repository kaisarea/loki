def index():
    images = db().select(db.image.ALL, orderby=db.image.title)
    comments = db().select(db.comment.ALL, orderby=db.comment.image_id)
    form = SQLFORM(db.comment)
    if form.process().accepted:
        response.flash = 'your comment is posted'
    return dict(images=images, comments=comments, form=form)

def show():
    image = db.image(request.args(0,cast=int)) or redirect(URL('index'))
    db.comment.image_id.default = image.id
    form = SQLFORM(db.comment)
    if form.process().accepted:
        response.flash = 'your comment is posted'
    comments = db(db.comment.image_id==image.id).select()
    return dict(image=image, comments=comments, form=form)

def download():
    return response.download(request, db)
