from django.shortcuts import render
import pandas as pd
import numpy as np

df = pd.read_json(
    "https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json")
# Create your views here.

# index page data for list of all countries and total infected


def index(request):
    confirmedGlobal = pd.read_csv(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()

    last_date = confirmedGlobal.columns[-1]
    barplotdata = confirmedGlobal[[
        'Country/Region', confirmedGlobal.columns[-1]]].groupby("Country/Region").sum()
    barplotdata.rename(
        columns={'Country/Region': 'Country/Region', last_date: 'values'}, inplace=True)

    barplotdata = barplotdata.sort_values(by='values', ascending=False)

    plotBar = barplotdata['values'].values.tolist()
    countryNames = barplotdata.index.tolist()

    jsonMapData = calcMapData(barplotdata, countryNames)
    displayMap = True
    context = {
        'totalCount': totalCount,
        'countryNames': countryNames,
        'plotBar': plotBar,
        'mapData': jsonMapData,
        'displayMap': displayMap
    }
    return render(request, 'index.html', context)

# views to produce map data


def calcMapData(barplotdata, countryNames):
    mapData = []
    for i in countryNames:
        try:
            tempDF = df[df['name'] == i]
            temp = {}
            temp['code3'] = list(tempDF['code3'].values)[0]
            temp['name'] = i
            temp['value'] = barplotdata[barplotdata.index == i]['values'].sum()
            temp['code'] = list(tempDF['code'].values)[0]
            mapData.append(temp)

        except:
            pass
    return mapData

# views for line chart for each country


def eachCountry(request):

    countryNameData = request.POST.get('countryName')

    confirmedGlobal = pd.read_csv(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()

    last_date = confirmedGlobal.columns[-1]
    barplotdata = confirmedGlobal[[
        'Country/Region', confirmedGlobal.columns[-1]]].groupby("Country/Region").sum()
    barplotdata.rename(
        columns={'Country/Region': 'Country/Region', last_date: 'values'}, inplace=True)

    barplotdata = barplotdata.sort_values(by='values', ascending=False)

    plotBar = barplotdata['values'].values.tolist()
    countryNames = barplotdata.index.tolist()

    displayMap = False

    rollingMean = rollingAverage(countryNameData, confirmedGlobal)
    axisValue = axisValues(countryNameData, confirmedGlobal)
    print(countryNameData, rollingMean)
    context = {
        'totalCount': totalCount,
        'countryNames': countryNames,
        'plotBar': plotBar,
        'displayMap': displayMap,
        'rollingMean': rollingMean,
        'countryName': countryNameData,
        'axisValue': axisValue
    }
    return render(request, 'index.html', context)


# Calculations or logic to find the rolling average
def rollingAverage(countryNameData, confirmedGlobal):
    countryDataSpe = pd.DataFrame(confirmedGlobal[confirmedGlobal['Country/Region']
                                                  == countryNameData][confirmedGlobal.columns[4:-1]].sum()).reset_index()
    countryDataSpe.columns = ['Date', 'values']
    countryDataSpe['lagVal'] = countryDataSpe['values'].shift(1).fillna(0)
    countryDataSpe['increamentVal'] = countryDataSpe['values'] - \
        countryDataSpe['lagVal']
    countryDataSpe['rollingMean'] = countryDataSpe['increamentVal'].rolling(
        window=4).mean()
    countryDataSpe = countryDataSpe.fillna(0)
    dataSetForLine = [{'label': 'Daily Cumulated Data', 'data': countryDataSpe['values'].values.tolist(), 'borderColor':'#3cba9f', 'fill':'false', },
                      {'label': 'Rolling Mean 4 Days', 'data': countryDataSpe['rollingMean'].values.tolist(), 'borderColor':'#c45850', 'fill':'false'}, ]
    return dataSetForLine


def axisValues(countryNameData, confirmedGlobal):
    countryDataSpe = pd.DataFrame(confirmedGlobal[confirmedGlobal['Country/Region']
                                                  == countryNameData][confirmedGlobal.columns[4:-1]].sum()).reset_index()
    countryDataSpe.columns = ['Date', 'values']
    countryDataSpe['lagVal'] = countryDataSpe['values'].shift(1).fillna(0)
    countryDataSpe['increamentVal'] = countryDataSpe['values'] - \
        countryDataSpe['lagVal']
    countryDataSpe['rollingMean'] = countryDataSpe['increamentVal'].rolling(
        window=4).mean()
    countryDataSpe = countryDataSpe.fillna(0)
    axisValueData = countryDataSpe.index.tolist()

    return axisValueData
