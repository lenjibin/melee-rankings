from liquipediapy.liquipediapy import liquipediapy

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

    def get_tournament_placements(self, tournament_link):
        spliced_link = tournament_link.replace("/smash/", "")
        soup, _ = self.liquipedia.parse(spliced_link)
        external_links = soup.find_all("a", class_="external text")
        for ext_link in external_links:
            maybe_start_gg_link = ext_link.get("href")
            if "start.gg" not in maybe_start_gg_link:
                continue
            start_gg_link = maybe_start_gg_link
            print(start_gg_link)            
        

m = melee("melee-rankings")
t = m.parse_tournaments_page()
m.get_tournament_placements(t[100]["link"])
print(t[0])


