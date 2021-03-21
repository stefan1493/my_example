import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import re


class FootballScrp():
    def __init__(self):
        url = 'https://www.soccerbase.com/teams/home.sd'
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')
        teams = soup.find('div', {'class': 'headlineBlock'}, text='Team').next_sibling.parent.find_all('li')
        competitions = soup.find('div', {'class': 'headlineBlock'},
                                 text='Competition').next_sibling.parent.find_all('li')
        self.teams_dict = {}
        self.competition_dict = {}
        self.comp_name = ""
        self.teams_var = ""
        self.choose_league(competitions)
        self.choose_teams(teams)
        self.extract_data()

    """ Method to choose a competition """
    def choose_league(self, competitions):
        competitions_dict = {}
        for i in competitions:
            competitions_dict[i.text] = i.find('a')['href'].rsplit('?', 1)[1]
            print(i.text)

        self.comp_name = input("Enter the league name: ")

        for k, v in competitions_dict.items():
            if self.comp_name == k:
                self.competition_dict[k] = v

        print(self.competition_dict)

    """ Method to choose a team or all teams form a certain competion """
    def choose_teams(self, teams):
        comp_id = self.competition_dict[self.comp_name]
        teams_founded=[]
        for i in teams:
            if comp_id == i.find('a')['href'].rsplit('&', 1)[1]:
                teams_founded.append(i)
                print(i.text)

        self.teams_var = input("Enter the league name(all/ a team): ")

        if self.teams_var != 'all':
            for i in teams_founded:
                if self.teams_var == i.text:
                    teams_founded = i

        if len(teams_founded)>1:
            for team in teams_founded:
                link = 'https://www.soccerbase.com' + team.find('a')['href']
                team = team.text
                self.teams_dict[team] = link
        else:
            link = 'https://www.soccerbase.com' + teams_founded.find('a')['href']
            team = teams_founded.text
            self.teams_dict[team] = link

    """ Method to extract data (V1)"""
    def extract_data(self):
        h_scores = []
        a_scores = []
        team = []
        comps = []
        dates = []
        h_teams = []
        a_teams = []
        for k, v in self.teams_dict.items():
            print('Acquiring %s data...' % k)

            headers = ['Team', 'Competition', 'Home Team', 'Home Score', 'Away Team', 'Away Score', 'Date Keep']
            r = requests.get('%s&teamTabs=results' % v)
            soup = bs(r.content, 'html.parser')

            # seasons = soup.find('div', {'class': 'seasonSelector clearfix'}, text='2019/20').next_sibling.parent.find_all('option')

            h_scores.extend([int(i.text) for i in soup.select('.score a em:first-child')])
            limit_scores = [int(i.text) for i in soup.select('.score a em + em')]
            a_scores.extend([int(i.text) for i in soup.select('.score a em + em')])

            limit = len(limit_scores)
            team.extend([k for i in soup.select('.tournament', limit=limit)])
            comps.extend([i.text for i in soup.select('.tournament a', limit=limit)])
            dates.extend([i.text for i in soup.select('.dateTime .hide', limit=limit)])
            h_teams.extend([i.text for i in soup.select('.homeTeam a', limit=limit)])
            a_teams.extend([i.text for i in soup.select('.awayTeam a', limit=limit)])

        df = pd.DataFrame(list(zip(team, comps, h_teams, h_scores, a_teams, a_scores, dates)),
                          columns=headers)
        print(df.groupby('Team').agg({'Home Score': 'mean', 'Away Score': 'mean'}))
        print(df.to_string())





    """ Not used in this moment """
    def teams_link(self, teams, competitions, comp_name):
        comp_id = '-'
        for i in competitions:
            if comp_name in i.text:
                comp_id = i.find('a')['href'].rsplit('?', 1)[1]
                break

        teams_founded=[]
        for i in teams:
            if comp_id == i.find('a')['href'].rsplit('&', 1)[1]:
                teams_founded.append(i)

        for team in teams_founded:
            link = 'https://www.soccerbase.com' + team.find('a')['href']
            team = team.text
            self.teams_dict[team] = link

if __name__== "__main__":
    FootballScrp()
    print('Finish')

