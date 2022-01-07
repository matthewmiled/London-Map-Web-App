def handle_uploaded_file(f):
    with open('/media/matt/image.jpeg', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)