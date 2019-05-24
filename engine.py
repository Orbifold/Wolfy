import atexit
import os

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr
from config import get_config


class Engine:
    def __init__(self):
        config = get_config()
        wolfram_path = config.get("DEFAULT", "WOLFRAM_PATH")
        self.image_path = os.path.join(os.getcwd(), 'static', 'city')
        atexit.register(self.cleanup)
        if wolfram_path is None or len(wolfram_path) == 0:
            self.session = WolframLanguageSession()
            print("Wolfram Engine session opened on default path.")
        else:
            self.session = WolframLanguageSession(wolfram_path)
            print(f"Wolfram Engine session opened on '{wolfram_path}'.")
        self._define_wolfram_functions()

    def _define_wolfram_functions(self):
        self.get_weather = self.session.function(wlexpr('<|"Temperature" -> WeatherData[#, "Temperature"], "WindSpeed" ->WeatherData[#,  "WindSpeed"],"Pressure"-> WeatherData[#,"Pressure"]|>&'))
        self.get_city = self.session.function(wlexpr('Module[{cities}, cities = TextCases[#, "City"];If[Length[cities] > 0, First[cities], ""]]&'))

    def test(self):
        self.check_session()
        return self.session.evaluate(wlexpr('NIntegrate[Sin[Sin[x]], {x, 0, 2}]'))

    def get_city_image(self, name):
        # search existing images if present
        lname = str.lower(name)
        for file in os.listdir(self.image_path):
            if file.endswith(".png"):
                if file == f"{lname}.png":
                    print(f"Found image for '{name}' in cache.")
                    return
        # get the image via websearch
        graphic = self.session.evaluate(wlexpr(f'WebImageSearch["{name}", "Images", MaxItems -> 1][[1]]'))

        path = os.path.join(self.image_path, f"{lname}.png")
        png_export = wl.Export(path, graphic, "PNG")
        return self.session.evaluate(png_export)

    def get_weather_info(self, text) -> dict:
        """
            Returns a dictionary with some weather info for the first city found in the given
            (natural language) text.
        :param text: any text
        """
        self.check_session()
        if text is None or len(text) == 0:
            return {}
        city = self.get_city(text)
        if city is None or len(city) == 0:
            return {}
        print(f"Found city: {city}")
        found = self.get_weather(city)

        if isinstance(found, dict) and found["Temperature"].args[0] != "NotAvailable":
            self.get_city_image(city)

            return {
                "Input": text,
                "City": city,
                "Temperature": found["Temperature"].args[0],
                "WindSpeed": found["WindSpeed"].args[0],
                "Pressure": found["Pressure"].args[0],
                "Info": self.session.evaluate(wlexpr(f'TextSentences[WikipediaData["{city}"]][[;; 5]]'))[0]
            }
        else:
            return {}

    def check_session(self):
        if self.session is None:
            raise Exception("The Engine is not present.")

    # noinspection PyBroadException
    def cleanup(self):
        """
            Note that there is no way to catch the SIGKILL
            and stop the engine gracefully if this happens.
        :return:
        """
        try:
            if self.session is not None:
                self.session.stop()
                print("Wolfram Engine stopped.")
        except Exception:
            pass
