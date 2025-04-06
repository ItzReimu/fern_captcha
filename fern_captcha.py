import random
import string
import io
from flask import Flask, session, request, render_template_string, send_file,render_template
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
# 安全密钥
app.secret_key = "helloferncaptcha12345"

# 字体文件路径
font_path = "C:\\Users\\Administrator\\Downloads\\YaHei.ttf"



def generate_captcha():
    characters = string.ascii_letters + string.digits
    captcha_text = ''.join(random.choice(characters) for _ in range(5))
    print("生成的验证码:", captcha_text)

    img_width = 150
    img_height = 50
    image = Image.new('RGB', (img_width, img_height), color='white')
    
    n = len(captcha_text)
    segment_width = img_width / n
    center_y = img_height // 2
    colour_list = ['black', 'red', 'blue', 'yellow', 'green', 'purple']

    for i, char in enumerate(captcha_text):
        font_size = random.randint(25, 31)
        font = ImageFont.truetype(font_path, font_size)
        angle = random.uniform(-45, 45)
        
        temp_size = (font_size * 3, font_size * 3)
        temp_image = Image.new('RGBA', temp_size, (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_image)
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
        pos_x = (temp_size[0] - char_width) // 2
        pos_y = (temp_size[1] - char_height) // 2
        temp_draw.text((pos_x, pos_y), char, font=font, fill=random.choice(colour_list))
        
        rotated = temp_image.rotate(angle, resample=Image.BICUBIC, center=(temp_size[0]//2, temp_size[1]//2))
        bbox_rotated = rotated.getbbox()
        if bbox_rotated is None:
            continue 
        cropped = rotated.crop(bbox_rotated)
        
        center_x = int(segment_width * (i + 0.5))
        paste_x = center_x - cropped.width // 2
        paste_y = center_y - cropped.height // 2
        
        if paste_x < 0:
            paste_x = 0
        if paste_y < 0:
            paste_y = 0
        if paste_x + cropped.width > img_width:
            paste_x = img_width - cropped.width
        if paste_y + cropped.height > img_height:
            paste_y = img_height - cropped.height
        
        image.paste(cropped, (paste_x, paste_y), cropped)

    draw = ImageDraw.Draw(image)
    for _ in range(random.randint(14, 18)): 
        x1, y1 = random.randint(0, img_width), random.randint(0, img_height)
        x2, y2 = random.randint(0, img_width), random.randint(0, img_height)
        draw.line([x1, y1, x2, y2], fill=random.choice(colour_list), width=2)

    for _ in range(random.randint(140, 180)):
        x, y = random.randint(0, img_width), random.randint(0, img_height)
        draw.point((x, y), fill=random.choice(colour_list))

    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return captcha_text, img_io

@app.route('/captcha')
def captcha():
    captcha_text, image_io = generate_captcha()
    session['captcha'] = captcha_text
    return send_file(image_io, mimetype='image/png')

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        user_input = request.form.get('captcha', '')
        real_captcha = session.get('captcha', '')
        if user_input.lower() == real_captcha.lower():
            message = "Success"
        else:
            message = "Error"
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)
