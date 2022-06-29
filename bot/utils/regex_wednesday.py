from dataclasses import dataclass
import nextcord
import re
from settings import *
from dataclasses import dataclass


@dataclass
class WednesdayLanguage:
    trigger: str
    response: str
    wrong_day: str
    scream: str = "aaaaaaaaaaAAAAAAAAAA**AAAAA**"
    trigger_day: int = 2


languages = dict(
    english=WednesdayLanguage(
        trigger="It is wednesday",
        response="my dudes",
        wrong_day="It appears you don't know how a calendar works. Do you require assistance with that?",
    ),
    german=WednesdayLanguage(
        trigger="Es ist Mittwoch",
        response="meine Kerle",
        wrong_day="Hast du keinen Kalender oder was?",
    ),
    polish=WednesdayLanguage(
        trigger="jest [sś]roda",
        response="o panowie",
        wrong_day="Co kurwa?",
    ),
    dutch=WednesdayLanguage(
        trigger="het is woensdag",
        response="mijn makkers",
        wrong_day="Wie heeft jouw agenda gekoloniseerd?",
    ),
    hungarian=WednesdayLanguage(
        trigger="szerda van",
        response="felebarátaim",
        scream="ááááááááááÁÁÁÁÁÁÁÁÁÁ**ÁÁÁÁÁ**",
        wrong_day="Naptár eladó - kell egy.",
    ),
    slovak=WednesdayLanguage(
        trigger="je streda",
        response="kamoši moji",
        wrong_day="Neviem kde si, ale tu v Slovinsku nie je streda.",
    ),
    serbocroatian=WednesdayLanguage(
        trigger="sr(e|i(je)?)da je",
        response="moji ljudi",
        wrong_day="Jebote, zar nemaš kalendar?",
    ),
    french=WednesdayLanguage(
        trigger="c'?est mercredi",
        response="mes mecs",
        wrong_day="Ceci n'est pas un mercredi",
    ),
    finnish=WednesdayLanguage(
        trigger="se on keskiviikko",
        response="kaverit",
        wrong_day="Unohditko kalenterin saunaan?",
    ),
    swedish=WednesdayLanguage(
        trigger="det är onsdag",
        response="mina bekanta",
        wrong_day="Svårt att läsa kalendern eller vadå?",
    ),
    swedish_friday=WednesdayLanguage(
        trigger="det är fredag",
        response="mina bekanta",
        wrong_day="Svårt att läsa kalendern eller vadå?",
        trigger_day=4,
    ),
    japanese=WednesdayLanguage(
        trigger="水曜日だ", response="お前ら", scream="ああああああ**ああああ**", wrong_day="何?"
    ),
    norwegian=WednesdayLanguage(
        trigger="det er onsdag",
        response="folkens",
        scream="ææææææææææÆÆÆÆÆÆÆÆÆÆ**ÆÆÆÆÆ**",
        wrong_day="Ikke nok oljepenger til en kalender eller?",
    ),
    spanish=WednesdayLanguage(
        trigger="es mi(e|é)rcoles",
        response="mis amigos",
        wrong_day="https://www.google.com/search?q=¿Qué+día+es+hoy?",
    ),
    romanian=WednesdayLanguage(
        trigger="(est|e|i|iî) miercuri",
        response="fraţii mei",
        wrong_day="Ar fi bine să iei un calendar înainte să trimit Aeggis după tine.",
    ),
    hebrew=WednesdayLanguage(
        trigger="היום יום רביעי",
        response="אחים שלי",
        scream="אאאאאאאאאאאאאאאאה",
        wrong_day="https://www.google.com/search?q=?איזה+יום+היום",
    ),
    lithuanian=WednesdayLanguage(
        trigger="jau tre[cč]iadienis",
        response="mano bičiuliai",
        wrong_day="Ką, teutonų ordinas pavogė jūsų kalendorių?",
    ),
)
