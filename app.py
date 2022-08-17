from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            amazon_url = "https://www.amazon.in/s?k=" + searchString
            uClient = uReq(amazon_url)
            amanzon_page=uClient.read()
            uClient.close()
            amazon_html=bs(amanzon_page,"html.parser")
            big_boxes = amazon_html.findAll("div", {"data-component-type": "s-search-result"})
            box = big_boxes[0]
            product_link = "https://www.amazon.in/" + box.div.div.div.div.div.div.div.span.a['href']
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
            product_request = requests.get(product_link,headers=headers)
            product_request.encoding='utf-8'
            product_html = bs(product_request.text, "html.parser")
            print(product_html)
            comment_boxes = product_html.find_all('div', {'data-hook': "review"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            try:
                for commentbox in comment_boxes:
                    review = {
                        'product': product_html.title.text.replace('Amazon.in: Electronics', '').strip(),
                        'title': commentbox.find('a', {'data-hook': 'review-title'}).text.strip(),
                        'ratings': float(commentbox.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars','').strip()),
                        'body': commentbox.find('span', {'data-hook': 'review-body'}).text.strip()
                    }
                reviews.append(review)
            except Exception as e:
                print(e)
            return render_template('results.html', reviews=reviews)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True,port=8000)
