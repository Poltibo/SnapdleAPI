import json
import datetime
import random
from typing import List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exception import APIMessage, CardNotFoundException
from model import CardData, GuessAnswer


def roll_card_of_the_day(card_pool):
    today = datetime.date.today()
    random.seed(int(f"{today.year}{today.month}{today.day}"))
    return card_pool[random.choice(list(card_pool.keys()))]


app = FastAPI(
    title="SnapdleAPI",
    version="0.0.1",
    description="""
Get card data and match pattern from 
    """
)

file = open("data/scrapped_cards_info.json")
cards = json.load(file)

# today = datetime.date.today()
# random.seed(int(f"{today.year}{today.month}{today.day}"))
# card_of_the_day = cards[random.choice(list(cards.keys()))]


@app.get(
    "/cards/{card_name}/data",
    response_model=CardData,
    response_description="Get the data for the card",
    status_code=200,
    responses={
        code: {"model": APIMessage, "description": desc}
        for code, desc in (
                (
                    404, "The card does not exist"
                ),
        )
    },
    tags=["card"]
)
def get_card_data(card_name: str):
    if card_name not in cards.keys():
        raise CardNotFoundException(card_name)
    return cards[card_name]


@app.get(
    "/cards/{card_name}/guess_answer",
    response_model=GuessAnswer,
    response_description="Get the data and colors for the user's submitted guess",
    status_code=200,
    responses={
        code: {"model": APIMessage, "description": desc}
        for code, desc in (
                (
                    404, "The card does not exist"
                ),
        )
    },
    tags=["card"]
)
def get_guess_answer(card_name: str):
    if card_name not in cards.keys():
        raise CardNotFoundException(card_name)

    card_of_the_day = roll_card_of_the_day(cards)

    colors = {}
    for crit in ["energy", "power"]:
        if card_of_the_day[crit] == cards[card_name][crit]:
            colors[crit+"_color"] = "green"
        elif card_of_the_day[crit] > cards[card_name][crit]:
            colors[crit+"_color"] = "red_up"
        else:
            colors[crit+"_color"] = "red_down"

    for crit in ["pool"]:  # , "ability_type", "gender", "species"]:
        if card_of_the_day[crit] == cards[card_name][crit]:
            colors[crit + "_color"] = "green"
        else:
            colors[crit + "_color"] = "red"

    if card_of_the_day["ability_type"] == cards[card_name]["ability_type"]:
        colors["ability_type_color"] = "green"
    elif len(set(card_of_the_day["ability_type"]).intersection(set(cards[card_name]["ability_type"]))) > 0:
        colors["ability_type_color"] = "orange"
    else:
        colors["ability_type_color"] = "red"

    return {"card_data": cards[card_name], "card_data_colors": colors}


@app.get(
    "/cards/card_of_the_day",
    response_model=CardData,
    response_description="Get the data for the card of the day",
    status_code=200,
    tags=["card"]
)
def get_card_of_the_day_data():
    return roll_card_of_the_day(cards)


@app.get(
    "/cards/card_list",
    response_model=List[str],
    response_description="Get the list of the possible cards",
    status_code=200,
    tags=["card"]
)
def get_card_of_the_day_data():
    return list(cards.keys())


@app.exception_handler(CardNotFoundException)
async def card_not_found_error_exception_handler(request: Request, exc: CardNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"404": str(exc)},
    )


