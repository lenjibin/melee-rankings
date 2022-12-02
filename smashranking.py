from liquipediapy.liquipediapy import liquipediapy
from graphqlclient import GraphQLClient
import math
import json
from math import erf, sqrt
from datetime import datetime, date, timezone
import calendar
import csv
import os
import time
from urllib.error import HTTPError, URLError

START_GG_TOKEN = "26752bdd0be387c2311963708fb968f4"

class melee():
    def __init__(self, appname):
        self.appname = appname
        self.liquipedia = liquipediapy(appname, "smash")
        self.__image_base_url = "https://liquipedia.net"

    def parse_tournaments_page(self):
        soup, _ = self.liquipedia.parse("Portal:Tournaments/All/Melee")
        rows = soup.find_all("div", class_="divRow")
        
        tournament_data = []
        for row in rows:
            tournament_name = row.find("b").a.string
            tournament_link = row.find("b").a.get("href")
            tournament_date = row.find("div", class_="EventDetails-Left-55").string
            tournament_data.append({
                "name": tournament_name,
                "link": tournament_link,
                "date": tournament_date,
            })
        return tournament_data

    def parse_tournaments_page(self, link):
        soup, _ = self.liquipedia.parse(link)
        rows = soup.find_all("div", class_="divRow")
        
        tournament_data = []
        for row in rows:
            tournament_name = row.find("b").a.string
            tournament_link = row.find("b").a.get("href")
            tournament_date = row.find("div", class_="EventDetails-Left-55").string
            tournament_data.append({
                "name": tournament_name,
                "link": tournament_link,
                "date": tournament_date,
            })
        return tournament_data

    def get_tournament_placements(self, tournament_link):
        spliced_link = tournament_link.replace("/smash/", "")
        soup, _ = self.liquipedia.parse(spliced_link)
        external_links = soup.find_all("a", class_="external text")
        for ext_link in external_links:
            maybe_start_gg_link = ext_link.get("href")
            if "start.gg" not in maybe_start_gg_link:
                continue
            start_gg_link = maybe_start_gg_link



RATINGS = ["A", "B", "C", "D", "E", "F"]
class RatingRequirements:
    def __init__(self, min_competitors, rated_players, rated_finishers, ratings_awarded):
        self.min_competitors = min_competitors
        self.rated_players = rated_players
        self.rated_finishers = rated_finishers
        self.ratings_awarded = ratings_awarded

E1 = RatingRequirements(6, [0, 0, 0, 0, 0, 0], [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], [0, 0, 0, 0, 1])
D1 = RatingRequirements(15, [0, 0, 0, 0, 4, 0], [(0, 0), (0, 0), (0, 0), (0, 0), 2], [0, 0, 0, 1, 3])
C1 = RatingRequirements(15, [0, 0, 2, 2, 2, 0], [(0, 0), (0, 0), (2, 8), (2, 8), (0, 0)], [0, 0, 1, 3, 4])
C2 = RatingRequirements(25, [0, 0, 0, 4, 4, 0], [(0, 0), (0, 0), (0, 0), (4, 8), (0, 0)], [0, 0, 1, 3, 4])
C3 = RatingRequirements(64, [0, 0, 0, 24, 12, 0], [(0, 0), (0, 0), (0, 0), (4, 8), (4, 12)], [0, 0, 4, 4, 8])
B1 = RatingRequirements(15, [0, 2, 2, 2, 0, 0], [(0, 0), (2, 8), (2, 8), (0, 0), (0, 0)], [0, 1, 3, 2, 2])
B2 = RatingRequirements(25, [0, 2, 2, 2, 0, 0], [(0, 0), (2, 8), (2, 8), (0, 0), (0, 0)], [0, 1, 3, 4, 4])
B3 = RatingRequirements(64, [0, 0, 24, 12, 0, 0], [(0, 0), (0, 0), (4, 8), (4, 12), (0, 0)], [0, 4, 4, 8, 16])
A1 = RatingRequirements(15, [2, 2, 2, 0, 0, 0], [(2, 8), (2, 8), (0, 0), (0, 0), (0, 0)], [1, 1, 2, 2, 2])
A2 = RatingRequirements(25, [2, 2, 2, 0, 0, 0], [(2, 8), (2, 8), (0, 0), (0, 0), (0, 0)], [1, 3, 4, 2, 2])
A3 = RatingRequirements(64, [0, 24, 12, 0, 0, 0], [(0, 0), (4, 8), (4, 12), (0, 0), (0, 0)], [4, 4, 8, 8, 8])
A4 = RatingRequirements(64, [12, 12, 12, 0, 0, 0], [(4, 8), (4, 12), (0, 0), (0, 0), (0, 0)], [8, 8, 8, 8, 16])

tournament_points = [100, 85, 70, 50, 35, 25, 15, 10, 8, 5, 3, 1]
MAX_TOURNAMENTS = 8

AllRatingRequirements = [A4, A3, A2, A1, B3, B2, B1, C3, C2, C1, D1, E1]#E1, D1, C1, C2, C3, B1, B2, B3, A1, A2, A3, A4]
PLAYERS = {}


class Tournament:
    def __init__(self, players, date):
        players.sort(key=lambda x : x.elo)
        self.number_top_placements = min(int((math.pow(2, math.floor(math.log2(len(players))) - 1))), 64)
        self.players = players
        self.points = 0
        self.date = date
        top_players = players[-self.number_top_placements:]

        self.tournament_rating = self.RateTournament()
        self.points = tournament_points[self.tournament_rating]

        #maybe for future stuff
        total_elo = 0
        total_standard_deviation = 0

        for player in top_players:
            total_elo += player.elo

        self.mean_elo = total_elo / self.number_top_placements

        for player in top_players:
            total_standard_deviation += (player.elo - self.mean_elo) * (player.elo - self.mean_elo)


        self.std_dev_elo = math.sqrt(total_standard_deviation/self.number_top_placements)
        if self.std_dev_elo == 0:
            self.std_dev_elo = 1
        self.id = -1


    def RateTournament(self):
        all_ratings = [0, 0, 0, 0, 0, 0]
        points = 0
        for player in self.players:
            all_ratings[player.rank] += 1
            points += pow(2.51188643151, player.rank) #this to the power of 5 == 100

        for rating_requirement_index in range(len(AllRatingRequirements)):
            rating_requirement = AllRatingRequirements[rating_requirement_index]
            if len(self.players) < rating_requirement.min_competitors:
                continue
            for rating_index in range(len(rating_requirement.rated_players)):
                if all_ratings[rating_index] < rating_requirement.rated_players[rating_index]:
                    break
                if rating_index == len(rating_requirement.rated_players)-1:
                    return rating_requirement_index

        self.points = points
        return -1

    def SetID(self, id):
        self.id = id

class Player:

    def __init__(self, name, rank, elo, tournaments):
        self.tournaments = tournaments
        self.characters = {}
        self.name = name
        self.elo = 1
        self.rank = rank
        self.tournament_points = []

    def __repr__(self):
        return self.name + " | " + str(self.rank)

    def AddTournament(self, tournament):
        self.tournaments.append(tournament)


def GetEntrants(slug):
    entrants_query = """
    query EventEntrants($slug: String!, $page: Int!, $perPage: Int!) {
      event(slug:$slug) {
        id
        name
            videogame {
              id
            }
        entrants(query: {
          page: $page
          perPage: $perPage
        }) {
          pageInfo {
            total
            totalPages
          }
          nodes {
            id
            participants {
              id
              gamerTag
            }
          }
        }
      }
    }
    """
    entrants_json = {}
    entrants_variables = {"slug": slug, "page": 1, "perPage": 500}
    formatted_slug = slug.replace("\"", "").replace("\'", "").replace("/", "").replace("*", "").replace("?", "")
    if os.path.exists("entrants_{}.json".format(formatted_slug)):
        f = open("entrants_{}.json".format(formatted_slug))
        entrants_json = json.load(f)
    else: 
        entrants_data = client.execute(query = entrants_query, variables = entrants_variables)
        entrants_json = json.loads(entrants_data)

        if entrants_json == None:
            return []
        if entrants_json["data"] == None or entrants_json["data"]["event"] == None or entrants_json["data"]["event"]["entrants"] == None:
            return []
        with open("entrants_{}.json".format(formatted_slug), "w") as outfile:
            json.dump(entrants_json, outfile)      
                  
    pages = int(entrants_json["data"]["event"]["entrants"]["pageInfo"]["totalPages"])
    tournament_entrants = []
    for i in range(1, pages + 1):

        entrants_variables["page"] = i
        page_json = {}
        if os.path.exists("page_{}.json".format(formatted_slug)):
            f = open("page_{}.json".format(formatted_slug))
            page_json = json.load(f)
        else: 
            page_data = client.execute(query = entrants_query, variables = entrants_variables)
            page_json = json.loads(page_data)  
            with open("page_{}.json".format(formatted_slug), "w") as outfile:
                json.dump(page_json, outfile)  

        event_id = page_json["data"]["event"]["id"]
        for entrant in page_json["data"]["event"]["entrants"]["nodes"]:
            if len(entrant["participants"]) == 0:
                continue
            if entrant["participants"][0]["gamerTag"] == None:
                continue
            player_id = entrant["participants"][0]["gamerTag"].replace(" | | ", " | ")
            player_id = player_id.replace(",", ".")
            player_id = player_id.split(" | ")[-1]

            if (player_id == "" or player_id == None):
                player_id = ""
            if player_id not in PLAYERS.keys():
                PLAYERS[player_id] = Player(player_id, 5, 1, [])
            PLAYERS[player_id].AddTournament(str(event_id))
            tournament_entrants.append(PLAYERS[player_id])

    return tournament_entrants

def GetPlacements(id, num):
    placements_query = """
    query EventStandings($eventId: ID!, $page: Int!, $perPage: Int!) {
      event(id: $eventId) {
        id
        name
        standings(query: {
          perPage: $perPage,
          page: $page
        }){
          nodes {
            placement
            entrant {
              id
              name
            }
          }
        }
      }
    }
    """
    placements_json = {}
    if os.path.exists("placement_{}.json".format(int(id))):
        f = open("placement_{}.json".format(int(id)))
        placements_json = json.load(f)
    else:
        placements_variables = {"eventId": id, "page": 1, "perPage": num}
        placements_data = client.execute(query = placements_query, variables = placements_variables)
        placements_json = json.loads(placements_data)    
        with open("placement_{}.json".format(int(id)), "w") as outfile:
            json.dump(placements_json, outfile)
    return placements_json

normal_dist_std_devs = {"0.125": .1572, "0.25": .319,"0.375":.4887, "0.5": .675, "0.625": .887, "0.75":1.15, "0.8125":1.319, "0.875":1.543, "0.90625":1.676, "0.9375":1.863, "0.953125":1.987, "0.96875":2.154, "0.9765625":2.266, "0.984375":2.416, "0.9921875":2.657}

ELO_CHANGE_ALPHA = 1
def player_elo_change(player, placement_elo):
    if placement_elo > player.elo:
        player.elo = player.elo + (placement_elo - player.elo) * ELO_CHANGE_ALPHA

def UpdateRankings(placements, tournament):
    for placement_info in placements["data"]["event"]["standings"]["nodes"]:
        player_id = placement_info["entrant"]["name"]

        placement = placement_info["placement"] 
        number_top_placements = tournament.number_top_placements
        placement_elo = normal_dist_std_devs[str(1-placement/number_top_placements)] * tournament.mean_elo + tournament.mean_elo
        player_elo_change(PLAYERS[player_id], placement_elo)

def TopRankings(ranks_awarded):
    rankings = []
    for i in range(len(ranks_awarded)):
        for j in range(ranks_awarded[i]):
            rankings.append(i)
    while len(rankings) < 64:
        rankings.append(5)
    return rankings

def ProcessTournament(placements, tournament):
    
    if tournament.tournament_rating == -1:
        return
    tournament_ranks_awarded = TopRankings(AllRatingRequirements[tournament.tournament_rating].ratings_awarded)
    for placement_info in placements["data"]["event"]["standings"]["nodes"]:
        player_id = placement_info["entrant"]["name"].replace(" | | ", " | ")
        player_id = player_id.split(" | ")[-1]
        player_id = player_id.replace(",", ".")
        placement = placement_info["placement"] 
        if placement > 64:
            continue

        if player_id in PLAYERS: #a player name can change if a TO does it manually between placements and registration?!?!?
            player = PLAYERS[player_id]
            points_earned = 1/placement * tournament.points
            tournament_data = (points_earned, tournament.date, tournament.id)
            to_remove = []
            for i in range(len(player.tournament_points)):
                if (calendar.timegm(datetime.now().timetuple()) - player.tournament_points[i][1]) > 3.154e+7:
                    to_remove.append(player.tournament_points[i])

            for i in to_remove:
                player.tournament_points.remove(i)

            if player.tournament_points:
                player.tournament_points.append(tournament_data)
            elif len(player.tournament_points) < MAX_TOURNAMENTS or points_earned > player.tournament_points[-1][0]:
                insert_index = len(player.tournament_points)
                while insert_index > 0 and points_earned > player.tournament_points[insert_index-1]:
                    insert_index -= 1
                player.tournament_points.insert(insert_index, tournament_data)
            if len(player.tournament_points) > MAX_TOURNAMENTS:
                player.tournament_points.pop()
            
            if PLAYERS[player_id].rank > tournament_ranks_awarded[placement-1]:
                PLAYERS[player_id].rank = tournament_ranks_awarded[placement-1]


    
HANSEN_START_GG_TOKEN = "Bearer 44a662ba3068ce56cd36a1d2e9e5cfd9"
client = GraphQLClient("https://api.start.gg/gql/alpha")
client.inject_token(HANSEN_START_GG_TOKEN)

def GetMeleeSlug(tournament_data):
    events = []
    if "data" not in tournament_data:
        return events
    tournament = tournament_data["data"]["tournaments"]["nodes"][0]
    tournament_slug = tournament["slug"]

    for event in tournament["events"]:
        event_name = event["name"].lower()
        if "melee" in event_name and ("singles" in event_name or "1v1" in event_name):
            event_slug = tournament_slug + "/event/" + event_name
            event_slug = event_slug.replace(" - ", "-")
            event_slug = event_slug.replace(" ", "-")
            event_slug = event_slug.replace("(", "")
            event_slug = event_slug.replace(")", "")
            event_slug = event_slug.replace("[", "")
            event_slug = event_slug.replace("]", "")
            events.append((event_slug, event["id"]))

    return events

def GetTournamentByName(name, time):
    tournament_query = """
    query Tournaments($name: String!, $page: Int!,  $perPage: Int!, $afterDate: Timestamp, $beforeDate: Timestamp) {
      tournaments(query: {
        perPage: $perPage
        page: $page

        filter: {
          name: $name
          past: true
          afterDate: $afterDate
          beforeDate: $beforeDate
          sortByScore: true
           videogameIds: [
             1
           ]
        }
      }) {
        nodes {
          id
          name
          startAt
          slug
          events {
            id
            name
          }
        }
      }    
    }
    """
    before_time = time + 345600
    tournament_variables = {"name": name, "page": 1, "perPage": 1, "afterDate":time, "beforeDate": before_time}# 4 days in seconds
    tournament_json = {}
    formatted_name = name.replace("\"", "").replace("\'", "").replace("/", "").replace("*", "").replace("?", "")
    if os.path.exists("tournament_{}.json".format(formatted_name)):
        f = open("tournament_{}.json".format(formatted_name))
        tournament_json = json.load(f)
    else:
        tournament_data = client.execute(query = tournament_query, variables = tournament_variables)
        tournament_json = json.loads(tournament_data)
        with open("tournament_{}.json".format(formatted_name), "w") as outfile:
            json.dump(tournament_json, outfile)

    return tournament_json

def ParseDate(date):
    year = date.split(', ')[1]
    month_day = date.split(', ')[0]
    month = month_day.split(" - ")[0]
    month, day = month.split(" ")
    return year, month, day

m = melee("melee-rankings")
t3 = m.parse_tournaments_page("Portal:Tournaments/All/Melee/Pre-2018")
t2 = m.parse_tournaments_page("Portal:Tournaments/All/Melee/2018-2020")
t1 = m.parse_tournaments_page("Portal:Tournaments/All/Melee")
months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr':4, 'May': 5, 'Jun':6, 'Jul':7, 'Aug': 8, 'Sep': 9, 'Oct':10, 'Nov':11, 'Dec':12}

t = t1 + t2 + t3
t.reverse()
skipped_tourneys = []
processed_tournaments = set()
def GetRanking(tournaments, skipped_tourneys):
    try:
        timenow = calendar.timegm(datetime.now().timetuple())
        start_t_index = 0
        files = os.listdir("players")
        load_file = ""
        players_files = []
        for file in files:
            if "Players" in file:
                players_files.append(file.replace("Players", "").replace(".csv", ""))
        players_files = sorted(players_files, key=lambda x : int(x))
            
        if len(players_files) > 0:
            load_file = "players/Players{}.csv".format(players_files[-1])
            start_t_index = int(players_files[-1]) + 1
            with open(load_file, 'r', newline='', encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                PLAYERS.clear()
                for row in reader:
                    PLAYERS[row[0]] = Player(row[0], int(row[1]), int(row[2]), row[3].split(","))

        for t_index in range(start_t_index, len(t)):
            print("{} / {}".format(t_index, len(t)))

            tournament = t[t_index]
            print(tournament)
            date = ParseDate(tournament["date"])

            tournament_time=datetime(int(date[0]), months[date[1]], int(date[2]), 0, 0, 0)
            epoch_time = calendar.timegm(tournament_time.timetuple())
            if epoch_time > timenow or epoch_time < 1425168000: 
                continue

            #time.sleep(1.5) #use if no local
            
            name = tournament['name']
            if name == None:
                continue
            tournament = GetTournamentByName(name, epoch_time)

            if "data" not in tournament or len(tournament["data"]["tournaments"]["nodes"]) < 1:
                skipped_tourneys.append(name)
                continue     
            
            tournament_id = tournament["data"]["tournaments"]["nodes"][0]["id"]   
            if tournament_id in processed_tournaments:
                continue
            processed_tournaments.add(tournament["data"]["tournaments"]["nodes"][0]["id"])

            slugs = GetMeleeSlug(tournament)

            if len(slugs) < 1:
                skipped_tourneys.append(name)
                continue

            entrants = GetEntrants(slugs[-1][0])
            if len(entrants) < 6:
                skipped_tourneys.append(name)
                continue
            tournament = Tournament(entrants, epoch_time)
            tournament.SetID(slugs[-1][1])
            placements = GetPlacements(slugs[-1][1], tournament.number_top_placements)
            ProcessTournament(placements, tournament)
            with open('players/Players{}.csv'.format(str(t_index)), 'w', newline='', encoding="utf-8") as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                for player_name in PLAYERS.keys():
                    player = PLAYERS[player_name]
                    tournaments_string = " | ".join(player.tournaments)
                    points_string = ""
                    player_elo = 0
                    for point in player.tournament_points:
                        player_elo += point[0]
                        p_string = " . ".join(map(str, point))
                        p_string = "( " + p_string + " )"
                        points_string += p_string + " | "

                    player.elo = player_elo
                    csv_row = "{name}, {rating}, {elo}, {tournaments}, {points}".format(name = player.name, rating = player.rank, elo = player.elo, tournaments = tournaments_string, points = points_string)
                    spamwriter.writerow(csv_row.split(","))
    except HTTPError as error:
        print("RETRYING")
        print(error)
        time.sleep(15)
        GetRanking(tournaments, skipped_tourneys)


GetRanking(t, skipped_tourneys)

