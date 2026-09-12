import json
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
}

def fetch_nba_rosters():
    # 1. 30 NBA Takımının Listesini Çek
    teams_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
    res = requests.get(teams_url, headers=HEADERS)
    data = res.json()

    teams_data = {}
    team_list = data["sports"][0]["leagues"][0]["teams"]

    print(f"Toplam {len(team_list)} NBA takımı bulundu. Kadrolar çekiliyor...\n")

    for item in team_list:
        team = item["team"]
        t_id = team["id"]
        abbr = team.get("abbreviation", "").lower()
        display_name = team.get("displayName")

        # 2. Her Takımın Roster Uç Noktasına Git
        roster_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{t_id}/roster"
        r_res = requests.get(roster_url, headers=HEADERS)

        if r_res.status_code != 200:
            print(f"Hata: {display_name} kadrosu çekilemedi.")
            continue

        r_data = r_res.json()
        players = []

        # NBA'de oyuncular 'athletes' listesinde döner
        for player in r_data.get("athletes", []):
            players.append({
                "n": player.get("fullName"),
                "p": player.get("position", {}).get("abbreviation", "N/A"),
                "jersey": player.get("jersey", "--"),
                "experience": player.get("experience", {}).get("years", 0),
                "height": player.get("displayHeight", "--"),
                "weight": player.get("displayWeight", "--")
            })

        teams_data[abbr] = {
            "id": t_id,
            "name": display_name,
            "roster": players
        }

        print(f"✓ {display_name} ({len(players)} Oyuncu)")
        time.sleep(0.2)

    # 3. JSON Olarak Kaydet
    with open("nba_rosters.json", "w", encoding="utf-8") as f:
        json.dump(teams_data, f, ensure_ascii=False, indent=2)

    # 4. Doğrudan HTML'e eklenebilecek JS dosyası olarak kaydet
    with open("nba_rosters.js", "w", encoding="utf-8") as f:
        f.write("const NBA_ROSTER_DATA = " + json.dumps(teams_data, ensure_ascii=False, indent=2) + ";")

    print("\nTamamlandı! 'nba_rosters.json' ve 'nba_rosters.js' dosyaları hazır.")

if __name__ == "__main__":
    fetch_nba_rosters()