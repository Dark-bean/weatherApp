from flask import Flask, render_template, request, abort, Response,url_for,flash,redirect,session
import urllib.parse, urllib.request, requests
import json, time,re
from jinja2 import Environment, PackageLoader, select_autoescape


app= Flask(__name__)
app.config['SECRET_KEY']='df0331cefc6c2b9a5d0208a726a5d1c0fd37324feba25506'



#filter that converts unix time to readable datetime
@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s) # datetime.datetime.fromtimestamp(s)



@app.route('/forecast', methods=['GET'])
def get_weather():
    lat_long=request.args['lat_long'] #latitude and longitude info from home_page function
    lat_long=session['lat_long']

    #need to turn 'lat_long" str into float
    splitLat = re.split("\s", lat_long)
    lat= float(splitLat[1][:len(splitLat[1])-1])
    longi= float(splitLat[3][:len(splitLat[3])-1])

    url2= 'https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&units=metric&appid=cc80750aceae96aadae5160475ecb810'.format(lat,longi)
    #handles the URL HTTP request
    request2 = urllib.request.Request(url2)
    opener = urllib.request.build_opener()
    response2 = opener.open(request2)
    jsonStr = response2.read()
        

    env=Environment(loader=PackageLoader("wApp"),autoescape=select_autoescape())
    env.filters['ctime']=timectime #adding my custom function to filters
    template= env.get_template("index.html")
    return template.render(title='Weather Application', data=json.loads(jsonStr.decode('utf-8')))




@app.route('/', methods=['GET', 'POST'])
def home_page():
    #uses a geocoing api to take in a city&country, then returns latitude and longitude


    if request.method == 'POST': #handles city and country info users send
        city = request.form['city']
        country = request.form['country']

        if not city:
            flash('city is required!')
        elif not country:
            flash('country is required!')
        else:
            api_url = 'https://api.api-ninjas.com/v1/geocoding?city={}&country={}'.format(city,country)
            response = requests.get(api_url + city, headers={'X-Api-Key': 'N9VFsiD8wyKHK03tSE9bng==Y2BYHS5idQ1Z4kql'})
            print(response.json())
            if response.status_code == requests.codes.ok and response.json():
                print("WHAT AM I DOING HERE\n")
                data= response.json()
                lat= data[0]['latitude']
                longi=data[0]['longitude']
            else:
                print("\nIM HERE\n")
                flash("NOT A CITY/Country")
                return redirect(url_for('home_page'))
               # print("Error:", response.status_code, response.text)
            
            lat_long = json.dumps({"latitude":lat, "longitude":longi})
            session['lat_long'] = lat_long #turning values into a json so I can pass it through "redirect"
            return redirect(url_for('get_weather',lat_long=lat_long))


    return render_template('home.html',title='Weather App Home')


if __name__== "__main__":
    app.run()