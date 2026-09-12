import json
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
}

def fetch_nfl_rosters():
    # 1. 32 Takımın listesini ve ID'lerini çek
    teams_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
    res = requests.get(teams_url, headers=HEADERS)
    data = res.json()
    
    teams_data = {}
    team_list = data["sports"][0]["leagues"][0]["teams"]

    print(f"Toplam {len(team_list)} takım bulundu. Kadrolar çekiliyor...")

    for item in team_list:
        team = item["team"]
        t_id = team["id"]
        abbr = team.get("abbreviation", "").lower()
        display_name = team.get("displayName")
        
        # 2. Her takımın kadro uç noktasına git
        roster_url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{t_id}/roster"
        r_res = requests.get(roster_url, headers=HEADERS)
        
        if r_res.status_code != 200:
            print(f"Hata: {display_name} kadrosu çekilemedi.")
            continue
            
        r_data = r_res.json()
        
        offense = []
        defense = []
        special = []

        # ESPN kadroyu "athletes" altında Offense/Defense/Special Teams olarak gruplar
        for group in r_data.get("athletes", []):
            group_name = group.get("position", "").lower()
            items = group.get("items", [])
            
            for player in items:
                p_info = {
                    "n": player.get("fullName"),
                    "p": player.get("position", {}).get("abbreviation", "N/A"),
                    "jersey": player.get("jersey", "--"),
                    "experience": player.get("experience", {}).get("years", 0)
                }
                
                if "offense" in group_name:
                    offense.append(p_info)
                elif "defense" in group_name:
                    defense.append(p_info)
                elif "special" in group_name:
                    special.append(p_info)

        teams_data[abbr] = {
            "id": t_id,
            "name": display_name,
            "offense": offense,
            "defense": defense,
            "special": special
        }
        
        print(f"✓ {display_name} ({len(offense)} Ofans, {len(defense)} Defans, {len(special)} Özel Takım)")
        time.sleep(0.3)  # Rate-limit koruması

    # 3. Elde edilen veriyi JSON olarak kaydet
    with open("nfl_rosters.json", "w", encoding="utf-8") as f:
        json.dump(teams_data, f, ensure_ascii=False, indent=2)

    print("\nİşlem tamamlandı! Veriler 'nfl_rosters.json' dosyasına yazıldı.")

if __name__ == "__main__":
    fetch_nfl_rosters()