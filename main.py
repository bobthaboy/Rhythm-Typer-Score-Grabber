from RhythmTyperAPI import RhythmTyperAPI
from time import sleep
import csv

rt = RhythmTyperAPI()


def map_scrape():
    print("Grabbing all beatmaps...")
    beatmaps = []
    command = rt.get_beatmaps()
    sleep(1)

    beatmaps.extend(command.beatmaps)

    while True:
        command = rt.get_beatmaps(cursor=command.next_cursor)
        sleep(1)

        beatmaps.extend(command.beatmaps)

        if not command.has_more:
            break
    return beatmaps


def rank_grabber(player, plays, beatmaps, rank):
    exclude = False
    scores = []
    i = 0
    length = sum(len(beatmap.difficulties) for beatmap in beatmaps)

    print(f"(y/n) exclude scores where you already tie #1? Warning: if not, the code will take {len(plays)}s longer.")
    if input("") == "y".lower():
        exclude = True
        length -= len(plays)

    for beatmap in beatmaps:
        for dif in beatmap.difficulties:
            if (exclude and beatmap.beatmap_id in [play.beatmap_id for play in plays]
                    and dif.difficulty_name in [play.difficulty for play in plays]):
                continue
            score = 0
            ranks = set()
            lb = rt.beatmap_leaderboard(beatmap_id=beatmap.beatmap_id, difficulty=dif.difficulty_name)
            sleep(1)
            for user in lb:
                ranks.add(user.score)
                if user.username == player.username:
                    score = user.score
            ordered = sorted(ranks, reverse=True)
            i += 1
            print(f"{i} / {length}")
            try:
                place = ordered[rank - 1]
                if place > score:
                    scores.append([score, place, beatmap, dif])
            except IndexError:
                continue

    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "score", f"rank_{rank}", "beatmap_id", "artist", "title", "difficulty", "mapper"
        ])

        for score in scores:
            beatmap = score[2]
            dif = score[3]
            writer.writerow([
                score[0],
                score[1],
                beatmap.beatmap_id,
                beatmap.beatmap_artist,
                beatmap.beatmap_title,
                dif.difficulty_name,
                beatmap.mapper
            ])


def cunny_grabber(player, plays, beatmaps, target):
    exclude = False
    scores = []
    i = 0
    length = sum(len(beatmap.difficulties) for beatmap in beatmaps)

    print(f"(y/n) exclude scores where you already tie #1? Warning: if not, the code will take {len(plays)}s longer.")
    if input("") == "y".lower():
        exclude = True
        length -= len(plays)

    for beatmap in beatmaps:
        for dif in beatmap.difficulties:
            if (exclude and beatmap.beatmap_id in [play.beatmap_id for play in plays]
                    and dif.difficulty_name in [play.difficulty for play in plays]):
                continue
            score = 0
            fuck_score = 0
            lb = rt.beatmap_leaderboard(beatmap_id=beatmap.beatmap_id, difficulty=dif.difficulty_name)
            sleep(1)
            for user in lb:
                if user.username == player.username:
                    score = user.score
                if user.username == target:
                    fuck_score = user.score
            scores.append([score, fuck_score, beatmap, dif])
            i += 1
            print(f"{i} / {length}")

    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "score", target, "beatmap_id", "artist", "title", "difficulty", "mapper"
        ])

        for score in scores:
            beatmap = score[2]
            dif = score[3]
            writer.writerow([
                score[0],
                score[1],
                beatmap.beatmap_id,
                beatmap.beatmap_artist,
                beatmap.beatmap_title,
                dif.difficulty_name,
                beatmap.mapper
            ])


def fc_grabber(player, beatmaps):
    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "beatmap_id", "artist", "title", "difficulty", "mapper", "my_combo", "notes", "misses", "best_combo"
        ])

        i = 0
        length = sum(len(beatmap.difficulties) for beatmap in beatmaps)

        for beatmap in beatmaps:
            for dif in beatmap.difficulties:
                lb = rt.beatmap_leaderboard(beatmap_id=beatmap.beatmap_id, difficulty=dif.difficulty_name)
                sleep(1)
                i += 1
                print(f"{i} / {length}")
                best_combo = max(c.combo for c in lb)
                notes = dif.tap_count + dif.hold_count * 2 + dif.typing_count
                notes = int(notes)
                for user in lb:
                    if user.username == player.username:
                        combo = user.combo
                        if combo < notes:
                            writer.writerow([
                                beatmap.beatmap_id, beatmap.beatmap_artist, beatmap.beatmap_title, dif.difficulty_name,
                                beatmap.mapper, combo, notes, user.miss, best_combo
                            ])


def main():
    with open("user_id.txt", "r") as file:
        user_id = file.readline().strip()

    if not user_id:
        print("Problem in user_id.txt. Please put your firebase uid in there.")
        exit()

    try:
        player = rt.get_user_profile(user_id)
        sleep(1)
        plays = rt.first_place_scores(user_id).scores
        sleep(1)
    except KeyError:
        print("Problem in user_id.txt. Please put your firebase uid in there.")
        exit()

    print("Alright boss, what are we doing today? Do you want:")
    print("1. Compare my scores to a rank on all map leaderboards")
    print("2. Compare my scores to a player on all map leaderboards")
    print("3. Return all my non-FC scores")

    command = input("")

    if command == "1":
        print("Return scores from which leaderboard position? (ex: \"1\" compares you to all first place scores.) ")
        try:
            rank = int(input())
            rank_grabber(player, plays, map_scrape(), rank)
        except ValueError:
            print(f"Hey dumbass, ever stop to think \"Huh, maybe that ain't a number?\"")
            print("Fuck you.")
            print("I'm closing the code.")
            exit()

    elif command == "2":
        print("Return scores from which player? (ex: \"andrew\". Case sensitive!)")
        target = input()
        cunny_grabber(player, plays, map_scrape(), target)

    elif command == "3":
        fc_grabber(player, map_scrape())

    else:
        print(f"well DAMN jackie, i can't {command}!")
        exit()


main()
print("Done! Check \"output.csv\", you should be able to convert it into an Excel spreadsheet.")
