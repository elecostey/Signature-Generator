from flask import Flask
from flask import request
from flask import render_template
import urllib, cStringIO
from PIL import Image
import httplib
import urlparse
import bcrypt
import time


app = Flask(__name__)

html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title></title>
      </head>

      <body>
        <div class="info" style=" padding: 8px 0 8px 8px; display: inline; font-family: Arial;">
            <div style="line-height: 1.4; font-weight: bold; font-size: 16px; margin: 0;">{0} {1}</div>
            <div style="line-height: 1.4; font-size: 14px; margin: 0 0 0 0; display: inline; color: #7f7c7c; ">{2}</div>
            <div style=" " >
              <img class="picture" src="{9}"  style="margin-bottom: -10px; margin-top: 10px;">
            </div>
            <p style="line-height: 1.6; font-size: 16px; margin: 20px 0 0 0;">{3}</p>
            <p style="line-height: 1.6; font-size: 14px; margin: 0 0 0 0; display: inline;">{4}</p>
            <br>
            <br>
            <div style="line-height: 1.6; font-weight: bold;  display: inline; font-size: 14px; color: #7f7c7c;">tel</div><div style="font-size: 14px; margin-left: 22px; display: inline;">{5}</div>
            <br>
            <div style="line-height: 1.6; font-weight: bold; display: inline; font-size: 14px;  color: #7f7c7c;">mob</div><div style="font-size: 14px; margin-left: 9px; display: inline;">{6}</div>
            <br>
            <div style="line-height: 1.6; font-weight: bold; display: inline; font-size: 14px;  color: #7f7c7c;">mail</div><div style="font-size: 14px; margin-left: 11px; display: inline;">{7}</div>
        </div>

        <br>
        <br>

        <div style="display: -webkit-flex; -webkit-flex-wrap: nowrap; display: flex; flex-wrap: nowrap;  ">
          <div style=" " >
            <img class="picture" src="{8}" alt="Antonela picture"   style="width:20vw; max-width:100px; margin-right:-2px; max-height: 136px; border-radius: 0 0 0 20px;">
          </div>
          <div style="">
            <img class="banner" src="https://www.borna-koruznjak.from.hr/projects/signature-images/banner3.jpg" alt="Antonela picture" ; style="width:70vw;  max-width:350px; border-radius: 0 20px 20px 0; ">
          </div>
        </div>

        <div style="display: block;">
          <a style="text-decoration: none; color: black;" href="http://www.porscheinterauto.hr/"><div style= "font-family: Arial; font-size: 14px; margin-top: 5px;">www.porcheinterauto.hr</div></a>
        </div>

      </body>
    </html>
"""

branches = [
    {
        'name': 'no branch',
        'url': ''
    },
    {
        'name': 'seat',
        'url': 'https://www.borna-koruznjak.from.hr/projects/signature-images/seat_logo.png'
    },
    {
        'name': 'audi',
        'url': 'https://www.borna-koruznjak.from.hr/projects/signature-images/audi_logo.png'
    },
    {
        'name': 'volkswagen',
        'url': 'https://www.borna-koruznjak.from.hr/projects/signature-images/volkswagen_logo.png'
    },
    {
        'name': 'gospodarska vozila',
        'url': 'https://www.borna-koruznjak.from.hr/projects/signature-images/gospodarska_logo.png'
    },
    {
        'name': 'dasweltauto',
        'url': 'https://www.borna-koruznjak.from.hr/projects/signature-images/dasweltauto_logo.png'
    },
    {
        'name': 'skoda',
        'url': 'https://www.borna-koruznjak.from.hr/projects/signature-images/skoda_logo.png'
    },
    {
        'name': 'porsche',
        'url': 'https://www.borna-koruznjak.from.hr/projects/signature-images/porsche_logo.png'
    }
]

error_message1 = 'Please fill in all the fields.'
error_message2 = 'The URL is not valid.'
error_message3 = 'The URL is not an image.'
error_message4 = 'The picture must be 100x137px. Please read info below.'


def get_user_input():
    name = request.form['name']
    surname = request.form['surname']
    job_title = request.form['job_title']
    company_name = request.form['company_name']
    address = request.form['address']
    tel = request.form['tel']
    mob = request.form['mob']
    email = request.form['email']
    picture_url = request.form['picture']
    user_branch = request.form.get('branch')
    branch_image_url = ' '

    for branch in branches:
        if user_branch == branch["name"]:
            branch_image_url = branch["url"]
            break

    keys = ['name', 'surname', 'job_title', 'company_name', 'address', 'tel', 'mob', 'email', 'picture_url',
            'branch_image_url', 'user_branch']
    requests = [name, surname, job_title, company_name, address, tel, mob, email, picture_url, branch_image_url, user_branch]
    user_inputs = {}
    for i in range(len(keys)):
        user_inputs[keys[i]] = requests[i]

    return user_inputs


def get_server_status_code(url):
    """
    Download just the header of a URL and
    return the server's status code.
    """
    host, path = urlparse.urlparse(url)[1:3]  # elems [1] and [2]
    try:
        conn = httplib.HTTPConnection(host)
        conn.request('HEAD', path)
        return conn.getresponse().status
    except StandardError:
        return None


def url_valid(url):
    """
    Check if a URL exists without downloading the whole file.
    We only check the URL header.
    """
    good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
    return get_server_status_code(url) in good_codes


def have_empty_entry():
    for entry in get_user_input():
        if len(get_user_input()[entry]) == 0:
            return True
    return False


def url_is_image(url):
    if url.find('.jpg') != -1 or url.find('.png') != -1 or url.find('.gif') != -1:
        return True
    return False


def image_size_valid(url):
    file = cStringIO.StringIO(urllib.urlopen(url).read())
    im = Image.open(file)
    width, height = im.size
    if width == 100 and height == 137:
        return True
    return False


def check_passwords_match(password, input):
    hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    if bcrypt.hashpw(input.encode('utf8'), hashed) == hashed:
        return True
    return False


def render_template_with_error(tmpl_name, error_message):
    if error_message == error_message1:
        return render_template(tmpl_name,
                               name=get_user_input()['name'],
                               surname=get_user_input()['surname'],
                               job_title=get_user_input()['job_title'],
                               company_name=get_user_input()['company_name'],
                               address=get_user_input()['address'],
                               tel=get_user_input()['tel'],
                               mob=get_user_input()['mob'],
                               email=get_user_input()['email'],
                               branch_image_url=get_user_input()['branch_image_url'],
                               user_branch=get_user_input()['user_branch'],
                               picture=get_user_input()['picture_url'],
                               error=error_message)

    return render_template(tmpl_name,
                           name=get_user_input()['name'],
                           surname=get_user_input()['surname'],
                           job_title=get_user_input()['job_title'],
                           company_name=get_user_input()['company_name'],
                           address=get_user_input()['address'],
                           tel=get_user_input()['tel'],
                           mob=get_user_input()['mob'],
                           email=get_user_input()['email'],
                           branch_image_url=get_user_input()['branch_image_url'],
                           user_branch=get_user_input()['user_branch'],
                           error=error_message)


@app.route('/form')
@app.route('/')
@app.route('/preview')
@app.route('/download')
def welcome():
    return render_template("welcome.html")


@app.route('/form', methods=['POST'])
def access_form():
    password = '1234'
    input_password = request.form['password']
    error_message = 'The password is incorrect'
    if check_passwords_match(password, input_password) is True:
        time.sleep(0.5)
        return render_template("form.html")
    return render_template("welcome.html", error=error_message)


@app.route('/preview', methods=['POST'])
def preview():
    if request.method == 'POST':
        if have_empty_entry() is True:
            return render_template_with_error("form.html", error_message1)

        if url_valid(get_user_input()['picture_url']) is False:
            return render_template_with_error("form.html", error_message2)

        if url_is_image(get_user_input()['picture_url']) is False:
            return render_template_with_error("form.html", error_message3)

        if image_size_valid(get_user_input()['picture_url']) is False:
            return render_template_with_error("form.html", error_message4)

        return render_template("signature-template.html",
                               name=get_user_input()['name'],
                               surname=get_user_input()['surname'],
                               job_title=get_user_input()['job_title'],
                               company_name=get_user_input()['company_name'],
                               address=get_user_input()['address'],
                               tel=get_user_input()['tel'],
                               mob=get_user_input()['mob'],
                               email=get_user_input()['email'],
                               picture=get_user_input()['picture_url'],
                               branch_image_url=get_user_input()['branch_image_url'],
                               user_branch=get_user_input()['user_branch'])


@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        if have_empty_entry() is True:
            return render_template_with_error("form.html", error_message1)

        if url_valid(get_user_input()['picture_url']) is False:
            return render_template_with_error("form.html", error_message2)

        if url_is_image(get_user_input()['picture_url']) is False:
            return render_template_with_error("form.html", error_message3)

        if image_size_valid(get_user_input()['picture_url']) is False:
            return render_template_with_error("form.html", error_message4)

        new_template = html_template.format(get_user_input()['name'],
                                            get_user_input()['surname'],
                                            get_user_input()['job_title'],
                                            get_user_input()['company_name'],
                                            get_user_input()['address'],
                                            get_user_input()['tel'],
                                            get_user_input()['mob'],
                                            get_user_input()['email'],
                                            get_user_input()['picture_url'],
                                            get_user_input()['branch_image_url'])
        return render_template("download.html", signature=new_template)

if __name__ == '__main__':
    app.debug = True
    app.run(host='192.168.1.87', port=5000)
