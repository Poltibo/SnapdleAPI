import json
import pandas as pd
from statistics import mean

from fastapi_views import get_guess_answer
from model import GuessAnswer

file = open("data/scrapped_cards_info.json")
cards = json.load(file)
df = pd.DataFrame(cards).transpose()
df = df.reset_index()

test_guess = {
  "card_data": {
    "card_id": 124,
    "name": "Lady Sif",
    "energy": 3,
    "power": 4,
    "pool": "Pool 1",
    "ability_type": [
      "discard",
      "on-reveal"
    ]
  },
  "card_data_colors": {
    "energy_color": "green",
    "power_color": "red_down",
    "pool_color": "red",
    "ability_type_color": "orange"
  }
}


def get_eligible_guesses(guess_answer):
    if guess_answer["card_data_colors"]["energy_color"] == "green":
        energy_cond = df["energy"].astype(int) == guess_answer["card_data"]["energy"]
    elif guess_answer["card_data_colors"]["energy_color"] == "red_down":
        energy_cond = df["energy"].astype(int) < guess_answer["card_data"]["energy"]
    else:
        energy_cond = df["energy"].astype(int) > guess_answer["card_data"]["energy"]

    if guess_answer["card_data_colors"]["power_color"] == "green":
        power_cond = df["power"].astype(int) == guess_answer["card_data"]["power"]
    elif guess_answer["card_data_colors"]["power_color"] == "red_down":
        power_cond = df["power"].astype(int) < guess_answer["card_data"]["power"]
    else:
        power_cond = df["power"].astype(int) > guess_answer["card_data"]["power"]

    if guess_answer["card_data_colors"]["pool_color"] == "green":
        pool_cond = df["pool"] == guess_answer["card_data"]["pool"]
    else:
        pool_cond = df["pool"] != guess_answer["card_data"]["pool"]

    if guess_answer["card_data_colors"]["ability_type_color"] == "green":
        ability_type_cond = df["ability_type"].apply(
            lambda x:  x == guess_answer["card_data"]["ability_type"]
        )
    elif guess_answer["card_data_colors"]["ability_type_color"] == "orange":
        ability_type_cond = df["ability_type"].apply(
            lambda x:  len(list(set(x) & set(guess_answer["card_data"]["ability_type"]))) != 0
        ) & df["ability_type"].apply(
            lambda x: x != guess_answer["card_data"]["ability_type"]
        )
        # ability_type_cond = len(list(set(df["ability_type"]) & set(guess_answer["card_data"]["ability_type"]))) != 0
    else:
        ability_type_cond = df["ability_type"].apply(
            lambda x: len(list(set(x) & set(guess_answer["card_data"]["ability_type"]))) == 0
        )
        # ability_type_cond = len(list(set(df["ability_type"]) & set(guess_answer["card_data"]["ability_type"]))) == 0

    return df.loc[(energy_cond & power_cond & pool_cond & ability_type_cond), :]


def get_eligible_guesses_number(guess_answer):
    return len(get_eligible_guesses(guess_answer))


def get_guess_answer_custom(guess_card: str, target_card: str):

    colors = {}
    for crit in ["energy", "power"]:
        if cards[target_card][crit] == cards[guess_card][crit]:
            colors[crit+"_color"] = "green"
        elif cards[target_card][crit] > cards[guess_card][crit]:
            colors[crit+"_color"] = "red_up"
        else:
            colors[crit+"_color"] = "red_down"

    for crit in ["pool"]:  # , "ability_type", "gender", "species"]:
        if cards[target_card][crit] == cards[guess_card][crit]:
            colors[crit + "_color"] = "green"
        else:
            colors[crit + "_color"] = "red"

    if cards[target_card]["ability_type"] == cards[guess_card]["ability_type"]:
        colors["ability_type_color"] = "green"
    elif len(set(cards[target_card]["ability_type"]).intersection(set(cards[guess_card]["ability_type"]))) > 0:
        colors["ability_type_color"] = "orange"
    else:
        colors["ability_type_color"] = "red"

    return {"card_data": cards[guess_card], "card_data_colors": colors}


def get_average_eligible_guesses(guess_card: str):
    l = []
    print(f"Computing guesses for {guess_card} as starter...")
    for target_card in cards.keys():
        print(f"{target_card}: {get_eligible_guesses_number(get_guess_answer_custom(guess_card, target_card))}")
        l.append(get_eligible_guesses_number(get_guess_answer_custom(guess_card, target_card)))
    return mean(l)


def get_eligible_guesses_left(guess_list):
    df_res = df.copy()
    for guess in guess_list:
        df_tmp = get_eligible_guesses(get_guess_answer(guess))
        card_id_tmp = df_tmp["card_id"].unique().tolist()
        df_res = df_res[df_res["card_id"].isin(card_id_tmp)]
    return df_res


def get_best_starter():
    d = {}
    for starter_card in cards.keys():
        d[starter_card] = get_average_eligible_guesses(starter_card)
    return dict(sorted(d.items(), key=lambda item: item[1]))


starters = get_best_starter()
get_eligible_guesses(get_guess_answer("Shuri"))
get_eligible_guesses_left(["Shuri", "Bishop"])

d = {}
for name in get_eligible_guesses(get_guess_answer("Shuri"))["name"]:
    d[name] = starters[name]
