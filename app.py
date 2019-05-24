from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_cors import CORS
from engine import Engine

app = Flask(__name__,
            static_url_path = '',
            static_folder = 'static',
            template_folder = 'templates')
CORS(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

engine = Engine()

def validate_key(data, key_name):
    if data is None:
        raise Exception("The body was not supplied.")
    if key_name in data.keys():
        return data[key_name]
    else:
        raise Exception(f"The body should contain the '{key_name}' key.")

@app.route('/')
def default_page():
    return render_template("index.html")


@app.route('/api/weather', methods = ['POST'])
def weather():

    try:
        data = request.json
        text = validate_key(data, "text")
        found = engine.get_weather_info(text)

        return jsonify(found)
    except Exception as exc:
        # logger.exception("API error")
        abort(500, description = exc)


if __name__ == '__main__':
    app.run()
