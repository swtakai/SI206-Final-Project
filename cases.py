import requests
import sqlite3
import json
import os
import country_converter as coco

#Run gdp.py first 4 times, then run cases.py 5 times
#Then run analysis.py once

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpCasesTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Cases (Date CHAR(10), United_States INTEGER, Russia INTEGER, Poland INTEGER, Norway INTEGER, Egypt INTEGER, New_Zealand INTEGER, Cuba INTEGER, Ghana INTEGER, Lebanon INTEGER, Uganda INTEGER)')
    all_cases = get_data(cur, conn, '2020-08-01', '2020-12-01')
    usa = all_cases[0]
    rus = all_cases[1]
    pol = all_cases[2]
    nor = all_cases[3]
    egy = all_cases[4]
    nzl = all_cases[5]
    cub = all_cases[6]
    gha = all_cases[7]
    lbn = all_cases[8]
    uga = all_cases[9]
    n = 0
    x = 25
    cur.execute('SELECT Date FROM Cases ORDER BY Date DESC LIMIT 1')
    try:
        last_entry = cur.fetchone()[0]
        for index in range(len(usa)):
            if usa[index][0] == last_entry:
                n = index + 1
                x = n + 25
    except:
        last_entry = 0
    for i in range(0,len(usa[n:x])):
        us = usa[n + i]
        date = us[0]
        us_cases = us[2]
        russia = rus[n + i]
        rus_cases = russia[2]
        poland = pol[n + i]
        pol_cases = poland[2]
        norway = nor[n + i]
        nor_cases = norway[2]
        egypt = egy[n + i]
        egy_cases = egypt[2]
        nz = nzl[n + i]
        nzl_cases = nz[2]
        cuba = cub[n + i]
        cub_cases = cuba[2]
        ghana = gha[n + i]
        gha_cases = ghana[2]
        lebanon = lbn[n + i]
        lbn_cases = lebanon[2]
        uganda = uga[n + i]
        uga_cases = uganda[2]
        cur.execute('INSERT INTO Cases(Date, United_States, Russia, Poland, Norway, Egypt, New_Zealand, Cuba, Ghana, Lebanon, Uganda) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (date, us_cases, rus_cases, pol_cases, nor_cases, egy_cases, nzl_cases, cub_cases, gha_cases, lbn_cases, uga_cases))

def setUpTotalCasesTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS CountryData (Country_ID INTEGER, Cases INTEGER, Recovered INTEGER, Population INTEGER)')
    all_data = country_data(cur, conn)
    n = 0
    x = 25
    cur.execute('SELECT Country_ID FROM CountryData ORDER BY Country_ID DESC LIMIT 1')
    try:
        last_entry = cur.fetchone()[0]
        for index in range(len(all_data)):
            if all_data[index][0] == last_entry:
                n = index + 1
                x = n + 25
    except:
        last_entry = 0

    for i in range(len(all_data[n:x])):
        data = all_data[n + i]
        ids = data[0]
        cases = data[1]
        recovered = data[2]
        population = data[3]
        cur.execute('INSERT INTO CountryData (Country_ID, Cases, Recovered , Population ) VALUES (?,?,?,?)', (ids, cases, recovered, population))    
    conn.commit()

def get_data(cur, conn, start_date, end_date):
    countries = []
    cur.execute(f'SELECT country FROM GDP ORDER BY GDP DESC')
    country_names = cur.fetchall()
    for row in range(0, 99, 10):
        countries.append(country_names[row][0])
    codes = coco.convert(names=countries, to='ISO3')
    request_url = f'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{start_date}/{end_date}'
    request = requests.get(request_url)
    jsons = json.loads(request.text)
    data = jsons.get('data')
    data_list = []
    i = 0
    for name in codes:
        dateCases = []
        for date in data:
            all_cases = data[date].get(codes[i])
            if all_cases is None:
                continue
            else:
                cases = all_cases.get('confirmed')
                dateCases.append((date, countries[i], cases))
        data_list.append(dateCases)
        i += 1
    return data_list

def country_data(cur, conn):
    cur.execute('SELECT Country_ID, Country FROM GDP')
    id_name = cur.fetchall()
    per_country = []
    
    url = 'https://covid-api.mmediagroup.fr/v1/cases'
    request = requests.get(url)
    jsons = json.loads(request.text)
    for country in jsons:
        for name in id_name:
            if country == 'US':
                country = 'United States'
            if country == 'Taiwan*':
                country = 'Taiwan'
            if country == name[1]:
                country_id = name[0]
                if country == 'United States':
                    country = 'US'
                if country == 'Taiwan':
                    country = 'Taiwan*'
                data = jsons[country].get('All')
                confirmed = data.get('confirmed')
                recovered = data.get('recovered')
                population = data.get('population')
                per_country.append((country_id, confirmed, recovered, population))
    return sorted(per_country)

def main():
    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    setUpCasesTable(cur, conn)
    setUpTotalCasesTable(cur, conn)
    conn.close()    

if __name__ == "__main__":
	main()