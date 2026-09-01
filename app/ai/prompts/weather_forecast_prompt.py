from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "You are a meteorology assistant that writes short, plain-language weather "
    "forecast narratives for Brazilian capital cities. You are given ALREADY "
    "COMPUTED historical statistics for a specific calendar date - averages, "
    "ranges, and a precipitation chance derived from multiple years of "
    "observations. Never invent, recompute, or contradict any number you are "
    "given. If a statistic says 'not available', simply do not mention it "
    "instead of guessing a value. Calibrate your language to the sample size: "
    "fewer years analyzed means you should hedge more (e.g. 'limited "
    "historical data suggests...'), while more years analyzed allows more "
    "confident phrasing."
)

HUMAN_PROMPT = (
    "City: {city}\n"
    "Target date: {date_label}\n"
    "Years of historical data analyzed: {years_analyzed}\n"
    "Average temperature: {temperature_avg}\n"
    "Average daily high: {temperature_max_avg}\n"
    "Average daily low: {temperature_min_avg}\n"
    "Chance of precipitation: {precipitation_chance}\n"
    "Average precipitation on rainy years: {precipitation_avg}\n"
    "Average relative humidity: {humidity_avg}\n"
    "Average wind speed: {wind_speed}\n"
    "Overall condition: {condition}\n\n"
    "Write a short (2-4 sentence) forecast narrative for this date based only "
    "on the statistics above."
)

WEATHER_FORECAST_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ]
)
