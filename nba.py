#!/usr/bin/python

import time
import requests
import datetime as date
from lxml import html
from tabulate import tabulate
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-s", "--standings", help="Show NBA standings", action="store_true", dest="standing")
parser.add_option("-b", "--boxscore", dest="boxid",
                  help="Show box score of a match ID")
parser.add_option("-y", "--yesterday", dest="minusDay",
                  help="Shows game scores of y days before today")
parser.add_option("-p", "--player", dest="player_name",
                  help="Get Player profile")

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
	def __init__(self, team1, team2, team1_players, team2_players, status):
		self.team1 = team1
		self.team2 = team2
		self.team1_players = team1_players
		self.team2_players = team2_players
		self.status = status

	def print_score(self):
		print("\n"+self.team1.team_name + " vs " + self.team2.team_name + ": " + self.status)
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
	player_name = player(row.xpath('th/div/a/text()'))
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

def player(list):
	return list[1] if len(list) == 2 else ""


def nbaBoxScore(box_id):
	url = "http://sports.yahoo.com"+box_id
	tree = SportsTree(url).tree
	visitor_name = tree.xpath('//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[1]/div/div[2]/div[1]/a/span/text()')[0]
	hometeam_name   = tree.xpath('//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[2]/div/div[2]/div[1]/a/span/text()')[0]
	match_status = tree.xpath('//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[3]/div/div[1]/div/text()')[0]

	visitor_scores = []
	vis_qtr_xpath = '//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td'
	for td in tree.xpath(vis_qtr_xpath):
		visitor_scores.append(td.text_content())

	visitor_total = 0
	for score in visitor_scores:
		if score.isdigit():
			visitor_total = visitor_total + int(score)

	visitor_scores.append(str(visitor_total))

	hometeam_scores = []
	home_qtr_xpath = '//*[@id="Col1-0-Boxscore"]/div[1]/div[3]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td'
	for td in tree.xpath(home_qtr_xpath):
		hometeam_scores.append(td.text_content())

	home_total = 0
	for score in hometeam_scores:
		if score.isdigit():
			home_total = home_total + int(score)

	hometeam_scores.append(str(home_total))

	team1 = TeamScore(visitor_name, visitor_scores)
	team2 = TeamScore(hometeam_name, hometeam_scores)

	# Players box score
	vis_starter = '//*[@id="Col1-0-Boxscore"]/div[3]/div/div/div[1]/div[2]/div/table/tbody/tr'
	vis_bench 	= '//*[@id="Col1-0-Boxscore"]/div[3]/div/div/div[1]/div[3]/div/table/tbody/tr'
	hom_starter = '//*[@id="Col1-0-Boxscore"]/div[3]/div/div/div[2]/div[2]/div/table/tbody/tr'
	hom_bench   = '//*[@id="Col1-0-Boxscore"]/div[3]/div/div/div[2]/div[3]/div/table/tbody/tr'

	visitor_players = playerList(tree.xpath(vis_starter)) + playerList(tree.xpath(vis_bench))
	home_players = 	  playerList(tree.xpath(hom_starter)) + playerList(tree.xpath(hom_bench))


	box_score = BoxScore(team1, team2, visitor_players, home_players, match_status)
	
	return box_score

def findPlayer(tree, result_xpath):
	search_result = tree.xpath(result_xpath)
	if search_result:
		player_url = tree.xpath(result_xpath)[0].get('href')
		name = tree.xpath(result_xpath+'/text()')[0]
		return (name, player_url)

def searchPlayer(isCurrent, player_url):
	tree = SportsTree(player_url).tree
	parsables = ['/p[1]']
	if isCurrent:
		parsables.append('/p[2]')

	title		=		('//*[@id="info"]/div[4]/div[1]/div', '/strong/text()')
	games 		=  		('//*[@id="info"]/div[4]/div[2]/div[1]', '/text()')
	points 		=	 	('//*[@id="info"]/div[4]/div[2]/div[2]', '/text()')
	rebounds  	=		('//*[@id="info"]/div[4]/div[2]/div[3]', '/text()')
	assists  	= 		('//*[@id="info"]/div[4]/div[2]/div[4]', '/text()')

	fg 			= 		('//*[@id="info"]/div[4]/div[3]/div[1]', '/text()')
	three_fg 	=		('//*[@id="info"]/div[4]/div[3]/div[2]', '/text()')
	ft 			=		('//*[@id="info"]/div[4]/div[3]/div[3]', '/text()')
	efg			=		('//*[@id="info"]/div[4]/div[3]/div[4]', '/text()')

	per 		=		('//*[@id="info"]/div[4]/div[4]/div[1]', '/text()')
	ws 			=		('//*[@id="info"]/div[4]/div[4]/div[2]', '/text()')

	fields = [title, games, points, rebounds, assists, fg, three_fg, ft, efg, per, ws]
	headers = ["", "GM", "PT", "RB", "AST", "FG%", "3FG%", "FT%", "eFG", "PER", "WS"]

	output = []
	for parsable in parsables:
		list = []
		for aField in fields:
			list.append(first(tree.xpath(aField[0]+parsable+aField[1])))
		output.append(list)

	output.append([])
	print(tabulate(output, headers = headers))
	return

def playerProfile(player_name):
	print("Searching for", player_name)
	base_url = 'http://www.basketball-reference.com'
	url = base_url+"/search/search.fcgi?search="+player_name
	tree = SportsTree(url).tree

	current_player_result_xpath = '//*[@id="players"]/div[1]/div[1]/strong/a'
	retired_player_result_xpath = '//*[@id="players"]/div[1]/div[1]/a'

	current = findPlayer(tree, current_player_result_xpath)
	retired = findPlayer(tree, retired_player_result_xpath)

	if current:
		print("Found active player\n", current[0])
		searchPlayer(True, base_url+current[1])
	elif retired:
		print("Found retired player\n", retired[0])
		searchPlayer(False, base_url+retired[1])
	else:
		print("Can't find player", player_name)
	
	return

def nbaScores(day):
	dayCount = int(day)
	url = "http://sports.yahoo.com/nba/scoreboard/"
	if dayCount > 0:
		prevDate = date.date.today() + date.timedelta(days=-dayCount)
		url = url+"?dateRange="+str(prevDate)
		print(url)
	tree = SportsTree(url).tree
	lists = ['//*[@id="scoreboard-group-2"]/div/ul/li', '//*[@id="scoreboard-group-1"]/div/ul/li']
	for list in lists:
		scores = []
		for row in tree.xpath(list):
			link = 'div/div[1]/a'
			game = 'div/div[1]/a/div/div/div/div[2]/div/'
			time = 'div/div/a/div/div/div/div[1]/div[2]/div/div/div/span/text()'

			visitor_city = row.xpath(game+'ul/li[1]/div[2]/div/span[1]/text()')[0]
			visitor_name = row.xpath(game+'ul/li[1]/div[2]/span/div/text()')[0]
			visitor_score = row.xpath(game+'ul/li[1]/div[3]/text()')[0]

			home_city = row.xpath(game+'ul/li[2]/div[2]/div/span[1]/text()')[0]
			home_name = row.xpath(game+'ul/li[2]/div[2]/span/div/text()')[0]
			home_score = row.xpath(game+'ul/li[2]/div[3]/text()')[0]
            
			match_status = ""
			match_status_value = row.xpath(time)

			if match_status_value:
				match_status = match_status_value[0]
                        
			match_link = row.xpath(link)[0].get("href")
			scores.append([visitor_city + " " + visitor_name, visitor_score])
			scores.append([home_city + " " + home_name, home_score])
			scores.append(["Result", match_status])
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
elif options.minusDay:
	nbaScores(options.minusDay)
elif options.player_name:
	playerProfile(options.player_name)
else:
	nbaScores(0)


