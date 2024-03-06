from flask import Flask, render_template, request
from selenium import webdriver
import multiprocessing, time 
from urllib import parse
app = Flask(__name__)

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("disable-gpu")
browser = webdriver.Chrome(options=options)

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/xss-1", methods=['GET'])
def xss_1():
    return render_template('xss-1.html')

@app.route("/xss-1/message", methods=['POST'])
def xss_1_message():
    # input = request.form['input']
    params = request.form.to_dict()
    user_input = xss_1_sanitizer(params['input'])
    # Admin will see the message
    
    # browser.get(f"http://localhost:8000/xss-1/message")
    # Cannot use the default implementation, see the comments in browser_post
    # Browser parameter is meant for invoking the POST request once per user-submitted POST request
    if "browser" not in params:
        browser_execute("http://localhost:8000/xss-1/message", {'input': user_input, 'browser': True}, 1)

    return render_template('xss-1-message.html', input=user_input)

@app.route("/xss-2", methods=['GET'])
def xss_2():
    return render_template('xss-2.html')

@app.route("/xss-2/friend", methods=['GET'])
def xss_2_friend():
    return render_template('xss-2-friend.html')

@app.route("/xss-2/share", methods=['POST'])
def xss_2_share():
    try:
        browser_execute(request.json['link'], {'browser': True}, 2)
    finally:
        return {'success': True}, 200

@app.route("/xss-3", methods=['GET'])
def xss_3():
    return render_template('xss-3.html')

@app.route("/xss-3/message", methods=['POST'])
def xss_3_message():
    params = request.form.to_dict()
    user_input = params['input']

    if "browser" not in params:
        browser_execute("http://localhost:8000/xss-3/message", {'input': user_input, 'browser': True}, 3)

    return render_template("xss-3-message.html", input=user_input)

################## HELPER METHODS ######################
def xss_1_sanitizer(input):
    while '<script' in input.lower():
        input = input.lower().replace('<script', '')

    while '</script' in input.lower():
        input = input.lower().replace('</script', '')

    while 'http' in input.lower():
        input = input.lower().replace('http', '')

    while '//' in input:
        input = input.replace('//', '')
    
    while '<img' in input:
        input = input.replace('<img', '')

    return input

def browser_execute(path, params, challenge):
    browser.get("http://localhost:8000/")
    # Set cookie for each challenge, as if we are actually "viewing" the site
    # The implementation using global variables does not work if there are multiple browsers
    # accessing the page, which changes the global value to some unexpected value
    if challenge == 1:
        browser.add_cookie({'name' : 'flag', 'value' : 'IFS4103{f1rSt_m4st3R_oF_XSS}'})
    elif challenge == 2:
        browser.add_cookie({'name' : 'flag', 'value' : 'IFS4103{s3c0ND_m4st3R_oF_XSS}'})
    elif challenge == 3:
        browser.add_cookie({'name' : 'flag', 'value' : 'IFS4103{tH1RD_m4st3R_oF_XSS}'})

    # lazy if else
    if challenge == 2:
        browser.get(path)
    else:
        # Execute script to submit a POST requst to a endpoint
        # From https://stackoverflow.com/questions/5660956/is-there-any-way-to-start-with-a-post-request-using-selenium
        browser.execute_script("""
        function post(path, params, method='post') {
            console.log(path);
            const form = document.createElement('form');
            form.method = method;
            form.action = path;
        
            for (const key in params) {
                if (params.hasOwnProperty(key)) {
                const hiddenField = document.createElement('input');
                hiddenField.type = 'hidden';
                hiddenField.name = key;
                hiddenField.value = params[key];
        
                form.appendChild(hiddenField);
            }
            }
        
            document.body.appendChild(form);
            form.submit();
        }
        
        post(arguments[1], arguments[0]);
        """, params, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)