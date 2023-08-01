from flask import Flask,request,jsonify
import requests
from datetime import date
from datetime import datetime
from datetime import timedelta
import pytz

tz_NY = pytz.timezone('America/New_York') 
datetime_NY = datetime.now(tz_NY)

ct=str(datetime_NY)[11:19]
app=Flask(__name__)

today=date.today()
yesterday=today-timedelta(days=1)

stock_dictionary={'Apple, INC.':'AAPL','Google':'GOOGL','Microsoft':'MSFT','Facebook':'META','Amazon':'AMZN',
                  'Samsung Electronics':'SSNLF','Synopsys, INC.':'SNPS','IBM':'IBM','Tesla':'TSLA','Intel Corporation':'INTC'}

@app.route('/', methods=['GET','POST'])
def currency_stock_news():
    data=request.get_json()

    if data['queryResult']['intent']['displayName'] == 'currency-converter':
        in_curr=data['queryResult']['parameters']['unit-currency']['currency']
        quant=data['queryResult']['parameters']['unit-currency']['amount']
        out_curr=data['queryResult']['parameters']['currency-name']
        url=f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={in_curr}&to_currency={out_curr}&apikey=W6GSXASKRWVJ0LGO'
        response=requests.get(url)
        response= response.json()
        con_fact=float(response['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        final_amt=round(quant*con_fact,2)
        push={'fulfillmentText':f'{quant:,} {in_curr} is {final_amt:,} {out_curr}, Exchange rate: {con_fact}'}
        return jsonify(push)
    
    elif data['queryResult']['intent']['displayName'] =='stock-summoner':
        company=data['queryResult']['parameters']['company']

        if (ct<'16:00:00') and (ct>'9:30:00'):
            url=f'https://realstonks.p.rapidapi.com/{stock_dictionary[company]}'
            headers = {
                "X-RapidAPI-Key": "c9eab3f074mshc0ce2704596ff5bp159ca5jsn65649bca4e0e",
                "X-RapidAPI-Host": "realstonks.p.rapidapi.com"}

            stock_response=requests.get(url,headers=headers)
            stock_response= stock_response.json()
            price=stock_response['price']
            change_point=stock_response['change_point']
            change_percentage=stock_response['change_percentage']
            total_vol=stock_response['total_vol']
            push={'fulfillmentText':f'''Current Stock Statistics for {company}\n
            Price: {price}\n
            Change Point: {change_point}\n
            Change Percentage: {change_percentage}\n
            Total Volume: {total_vol}'''}

        else:
            date_time=data['queryResult']['parameters']['date-time']
            dt=''
            if date_time[:10]==str(today):
                dt=str(today)
            elif date_time[:10]=='':
                dt=str(today)
            elif any('endDate' in i for i in date_time):
                return jsonify({'fulfillmentText':'I can\'t do that yet'})
            else:
                pass

            url=f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_dictionary[company]}&apikey=W6GSXASKRWVJ0LGO'
            stock_response=requests.get(url)
            stock_response= stock_response.json()
            stock_data=stock_response['Time Series (Daily)'][dt]
            opening=stock_data['1. open']
            high=stock_data['2. high']
            low=stock_data['3. low']
            closing=stock_data['4. close']
            volume=stock_data['5. volume']
            push={'fulfillmentText':f'''Today's Stock Statistics for {company} on {str(today)} (All prices in USD)\n
            Opening Price: {opening}\n
            High Price: {high}\n
            Low Price: {low}\n
            Closing Price: {closing}\n
            Volume: {int(volume):,}'''}
            return jsonify(push)
    
    elif data['queryResult']['intent']['displayName'] =='news-fetcher':
        company=data['queryResult']['parameters']['company']
        url=f'https://newsapi.org/v2/everything?q={company}&from={str(yesterday)}&to={str(today)}&sortBy=popularity&apiKey=30ce921c99cf42dcb765670bf99aa3fc'
        article_response=requests.get(url)
        article_response= article_response.json()
        news_article=''
        for i in range(len(article_response['articles']))[:10]:
            title=article_response['articles'][i]['title']
            url=article_response['articles'][i]['url']
            news_article=news_article+f'''{title}\n{url}\n\n'''
        push={'fulfillmentText':news_article}
        return jsonify(push)









    




if __name__=='__main__':
    app.run(debug=True)
