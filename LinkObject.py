class LinkObject:
    def __init__(self, title='', price='', link='', photos=[]):
        self.title = title
        self.price = price
        self.link = link
        self.photos = photos

    def to_html(self):
        photoImgTags = ''.join(list(map(lambda photo: f'<img src="{photo}">', self.photos)))
        return f'''<hr>
        <a href="{self.link}">
            <h1>{self.title}</h1>
        </a>
        <h2><span style="color: #F00; font-weight: bold">{self.price}</span></h2>
        <div>
            {photoImgTags}
        </div>
        <hr>
        '''
