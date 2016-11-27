#!/usr/bin/python

import time, requests
from lxml import html
from tabulate import tabulate
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-s", "--standings", help="Show NBA standings", action="store_true", dest="standing")
parser.add_option("-b", "--boxscore", dest="boxid",
                  help="Show box score of a match ID")

(options, args) = parser.parse_args()

class TeamScore:
	def __init__(self, team_name, scores_quarter):
		self.team_name = team_name
		self.scores_quarter = scores_quarter

class PlayerScore:
	headers = [ "", "MIN", "PT", "FG", "3FG", "FT", "REB", "AST", "TO", "BLK", "STL", "PF", "+/-" ]
	def __init__(self, player_name, mins, pt, fg, three_fg, ft, reb, asst, to, blk, stl, pf, pm):
		self.player_name = player_name
		self.mins = mins
		self.pt = pt
		self.fg = fg
		self.three_fg = three_fg
		self.ft = ft
		self.reb = reb
		self.asst = asst
		self.to = to
		self.blk = blk
		self.stl = stl
		self.pf = pf
		self.pm = pm

	def printableList(self):
		return [ self.player_name, self.mins, self.pt, self.fg, self.three_fg, self.ft, self.reb, self.asst, self.to, self.blk, self.stl, self.pf, self.pm]

class BoxScore:
	def __init__(self, team1, team2, team1_players, team2_players):
		self.team1 = team1
		self.team2 = team2
		self.team1_players = team1_players
		self.team2_players = team2_players

	def print_score(self):
		print(self.team1.team_name, " vs ", self.team2.team_name)
		print(tabulate([self.team1.scores_quarter, self.team2.scores_quarter]))

		players = []
		players.append([self.team1.team_name])
		players.append([])
		for player in self.team1_players:
			players.append(player.printableList())
		players.append([self.team2.team_name])
		players.append([])		
		for player in self.team2_players:
			players.append(player.printableList())
		print(tabulate(players, headers = PlayerScore.headers))
		

class SportsTree:
	def __init__(self, url):
		page = requests.get(url)
		self.tree = html.fromstring(page.content)

def playerList(playerlist_xpath):
	players = []
	for row in playerlist_xpath:
		players.append(playerScore(row))
	return players
def playerScore(row):
	player_name = first(row.xpath('th/div/a/text()'))
	mins 		= first(row.xpath('td[1]/text()'))
	pt 			= first(row.xpath('td[14]/text()'))
	fg 			= first(row.xpath('td[2]/text()'))
	three_fg 	= first(row.xpath('td[3]/text()'))
	ft 			= first(row.xpath('td[4]/text()'))
	reb 		= first(row.xpath('td[7]/text()'))
	asst 		= first(row.xpath('td[8]/text()'))
	to 			= first(row.xpath('td[9]/text()'))
	blk 		= first(row.xpath('td[11]/text()'))
	stl 		= first(row.xpath('td[10]/text()'))
	pf 			= first(row.xpath('td[12]/text()'))
	pm 			= first(row.xpath('td[13]/text()'))

	player_score = PlayerScore(player_name, mins, pt, fg, three_fg, ft, reb, asst, to, blk, stl, pf, pm)

	return player_score

def first(list):
	return list[0] if any(list) else ""


def nbaBoxScore(box_id):
	url = "http://sports.yahoo.com"+box_id
	tree = SportsTree(url).tree
	visitor_name = tree.xpath('//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[1]/div/div[2]/div[1]/a/span/text()')[0]
	hometeam_name   = tree.xpath('//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[2]/div/div[2]/div[1]/a/span/text()')[0]

	visitor_scores = []
	vis_qtr_xpath = '//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td'
	for td in tree.xpath(vis_qtr_xpath):
		visitor_scores.append(td.text_content())

	hometeam_scores = []
	home_qtr_xpath = '//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td'
	for td in tree.xpath(home_qtr_xpath):
		hometeam_scores.append(td.text_content())

	team1 = TeamScore(visitor_name, visitor_scores)
	team2 = TeamScore(hometeam_name, hometeam_scores)

	# Players box score
	vis_starter = '//*[@id="Col1-0-Boxscore"]/div[4]/div/div/div[1]/div[2]/div/table/tbody/tr'
	vis_bench 	= '//*[@id="Col1-0-Boxscore"]/div[4]/div/div/div[1]/div[3]/div/table/tbody/tr'
	hom_starter = '//*[@id="Col1-0-Boxscore"]/div[4]/div/div/div[2]/div[2]/div/table/tbody/tr'
	hom_bench   = '//*[@id="Col1-0-Boxscore"]/div[4]/div/div/div[2]/div[3]/div/table/tbody/tr'

	visitor_players = playerList(tree.xpath(vis_starter)) + playerList(tree.xpath(vis_bench))
	home_players = 	  playerList(tree.xpath(hom_starter)) + playerList(tree.xpath(hom_bench))

	box_score = BoxScore(team1, team2, visitor_players, home_players)
	
	return box_score



def nbaScores():
	url = "http://sports.yahoo.com/nba/scoreboard/"
	tree = SportsTree(url).tree
	lists = ['//*[@id="scoreboard-group-2"]/div/ul/li', '//*[@id="scoreboard-group-1"]/div/ul/li']
	for list in lists:
		scores = []
		for row in tree.xpath(list):
			link = 'div/div[1]/a'
			game = 'div/div[1]/a/div/div/div/div[2]/div/'

			visitor_city = row.xpath(game+'ul/li[1]/div[2]/div/span[1]/text()')[0]
			visitor_name = row.xpath(game+'ul/li[1]/div[2]/span/div/text()')[0]
			visitor_score = row.xpath(game+'ul/li[1]/div[3]/text()')[0]

			home_city = row.xpath(game+'ul/li[2]/div[2]/div/span[1]/text()')[0]
			home_name = row.xpath(game+'ul/li[2]/div[2]/span/div/text()')[0]
			home_score = row.xpath(game+'ul/li[2]/div[3]/text()')[0]

			match_link = row.xpath(link)[0].get("href")
			scores.append([visitor_city + " " + visitor_name, visitor_score])
			scores.append([home_city + " " + home_name, home_score])
			scores.append(["box score", match_link])
			scores.append(["", ""])
		print(tabulate(scores))

	return

def nbaStandings():
	url  = "https://sports.yahoo.com/nba/standings/?selectedTab=CONFERENCE"
	tree = SportsTree(url).tree
	east = tree.xpath('//*[@id="Col1-0-LeagueStandings-Proxy"]/div/div[2]/table[1]/tbody/tr')
	west = tree.xpath('//*[@id="Col1-0-LeagueStandings-Proxy"]/div/div[2]/table[2]/tbody/tr')
	name_xpath = 'td[1]/div/div/a/span[2]/text()'
	win_xpath  = 'td[2]/text()'
	loss_xpath = 'td[3]/text()'
	printConference("East", east, name_xpath, win_xpath, loss_xpath)
	printConference("West", west, name_xpath, win_xpath, loss_xpath)
	return

def printConference(conference, tree, name_xpath, win_xpath, loss_xpath):
	print(conference)
	list = []
	for i, row in enumerate(tree):
		t = row.xpath(name_xpath)[0]
		w = row.xpath(win_xpath)[0]
		l = row.xpath(loss_xpath)[0]
		team = [i+1, t, w, l]
		list.append(team)
	print(tabulate(list, headers=["Rank", "Team", "Win", "Loss"], tablefmt="simple"))
	return

# nbaScores()
if options.standing:
	nbaStandings()
elif options.boxid:
	box_score = nbaBoxScore(options.boxid)
	box_score.print_score()
else:
	nbaScores()


