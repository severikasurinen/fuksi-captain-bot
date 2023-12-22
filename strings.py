"""
This file contains all messages visible to users, with translations.
"""


START_MSG = {'fi': """Tiedotteet tilattu! Lähettämällä viestejä tänne, tulevat ne näkyviin anonyymisti molemmille kippareille. /-komennot eivät kuitenkaan näy kippareille.
             
Käytä komentoa /aiemmat listataksesi kaikki aiemmat tiedotteet. Komennolla /help, saat tarkempia ohjeita botin käytöstä.""",

             'en': """Announcements subscribed! By sending messages here, they will be sent anonymously to both fuksi captains. / commands will, however, not be sent to the captains.
             
Use command /previous to list all previous announcements. Use /help to get further instructions on using the bot."""}


HELP_MSG = {'fi': """Lähettämällä viestejä tänne, tulevat ne näkyviin anonyymisti molemmille fuksikippareille. /-komennot eivät kuitenkaan näy kippareille.

<b>KOMENNOT</b>
-
/info - Kertoo tärkeää tietoa.
/laulu - Testaa kuinka hyvin osaat teekkarilaulujen sanat.
/fakta - Kertoo viikon teekkarifaktan.
/aiemmat - Listaa kaikki aiemmat tiedotteet.
/exit - Poistaa botin toiminnot käytöstä ja peruu tiedotteiden tilauksen.""",

            'en': """By sending messages here, they will be sent anonymously to both fuksi captains. / commands will, however, not be sent to the captains.

<b>COMMANDS</b>
-
/info - Tells you important information.
/song - Tests how well you know the lyrics of teekkari songs.
/fact - Tells you the teekkari fact of the week.
/previous - Lists all the previous announcements.
/exit - Disables bot commands and announcements."""}


HELP_MSG_ADMIN = """

<b>ADMINS</b>
-
/broadcast [Message] - Broadcasts and pins the message to users. Accepts text, photo, and video.
/broadcast_temp [Message] - Similar to broadcast, but without saving in previous broadcasts.
/edit [Message] - Replace text in previous announcement. Does not work for photos and video!
/delete - Deletes previous announcement. Does not work for photos and video!
/forward - Enables forwarding mode. Broadcasts message forwarded to the bot within the next 60 s.
/forward_temp - Similar to forward, but without saving in previous broadcasts.
/users - Tells you the number of users.
/fuksi [Year] - Replies with an image of a random fuksi of desired year, captioned with their name.
/ update_bot - Updates bot and backs up IDs. <b>AVOID USE!!!</b>
/ reboot_server - Reboots server. <b>AVOID USE!!!</b>"""


INFO_MSG = {'fi': """Alle on koottu tärkeitä linkkejä ja yhteystietoja.

<a href="https://www.fyysikkokilta.fi/"><b>KILTA</b></a>
- <a href="https://www.fyysikkokilta.fi/fuksina-killassa/">Fuksina killassa</a>
- <a href="https://www.fyysikkokilta.fi/fuksiaapinen/">Fuksiaapinen</a>
- <a href="https://www.fyysikkokilta.fi/tapahtumakalenteri/">Tapahtumakalenteri</a>
- <a href="https://www.fyysikkokilta.fi/fyysikkokillan-hairintayhdyshenkilot/">Killan häirintäyhdyshenkilöt</a>

<a href="https://www.aalto.fi/fi"><b>KOULU</b></a>
- <a href="https://www.aalto.fi/fi/ohjelmat/teknistieteellinen-kandidaattiohjelma/opintojen-aloittaminen">Opintojen aloittaminen</a>
- <a href="https://www.aalto.fi/fi/ohjelmat/teknistieteellinen-kandidaattiohjelma/mallilukujarjestykset#0-lukuvuosi-2023-2024">Mallilukujärjestys</a>
- <a href="https://www.aalto.fi/fi/opiskelijan-opas">Opiskelijan opas</a>
- Opiskelijapalvelut: opiskelijapalvelut@aalto.fi
- <a href="https://www.aalto.fi/fi/palvelut/it-palvelut">IT-palvelut</a>
- <a href="https://www.ayy.fi/fi">AYY</a>
- <a href="https://kanttiinit.fi/">Kampusravintolat</a>
- <a href="https://www.yths.fi/yths/ylioppilaiden-terveydenhoitosaatio/">Terveydenhuolto</a>
- <a href="https://www.tenttiarkisto.fi/">Tenttiarkisto</a>""",

            'en': """Below is a summary of important links and contact information

<a href="https://www.fyysikkokilta.fi/en"><b>GUILD</b></a>
- <a href="https://www.fyysikkokilta.fi/en/fuksina-killassa/">As a fuksi in the guild</a>
- <a href="https://www.fyysikkokilta.fi/en/fuksiaapinen/">Fuksi Guidebook</a>
- <a href="https://www.fyysikkokilta.fi/en/tapahtumakalenteri/">Event calendar</a>
- <a href="https://www.fyysikkokilta.fi/en/fyysikkokillan-hairintayhdyshenkilot/">Guild harassment contact persons</a>

<a href="https://www.aalto.fi/en"><b>SCHOOL</b></a>
- <a href="https://www.aalto.fi/en/programmes/aalto-bachelors-programme-in-science-and-technology/starting-your-studies">Starting your studies</a>
- <a href="https://www.aalto.fi/en/programmes/aalto-bachelors-programme-in-science-and-technology/recommended-timetable">Recommended timetable</a>
- <a href="https://www.aalto.fi/en/student-guide">Student Guide</a>
- Student Services: opiskelijapalvelut@aalto.fi
- <a href="https://www.aalto.fi/en/services/it-services">IT Services</a>
- <a href="https://www.ayy.fi/en">AYY</a>
- <a href="https://kanttiinit.fi/">Campus restaurants</a>
- <a href="https://www.yths.fi/en/fshs/finnish-student-health-service/">Health services</a>
- <a href="https://www.tenttiarkisto.fi/">Exam archive</a>"""}


LYRICS = { "Teekkarihymni": """:,: Yö kuin sielu teekkarin on pimiä,
takajoukko nukkuu vain, nukkuu vain.
Tarhapöllön ääni kimiä
kuuluu pappilasta päin, kuuluu päin.
Ja taas, ja siis, ja
1, 2, 3, 4, 5. :,:""",

          "Oh Lord": """:,: Oh Lord, it's hard to be humble,
when you're perfect in every way.
I can't wait to look in the mirror,
'cause I get better looking each day.
To know me is to love me,
I must be a hell of a man,
Oh Lord it's hard to be humble,
but I'm doing the best I can. :,:""",

          "Ikuisen teekkarin laulu": """Talvi-iltain tummentuessa
Polin suojiin me saavumme taas.
:,: Meidät tekniikka jälkeen on jättänyt,
sen me tahdomme unhoittaa. :,:

Unelma vain on diplomityömme,
joka tenttimme vanhennut.
:,: Jo ruostunut harpikko käyttämätön,
tushi pulloihin jähmennyt. :,:

Aina teekkaripolvien uutten
ohi pöytämme käyvän nään.
:,: Mutta meillä ei voimaa enää kylliksi
heidän joukkoonsa liittymään. :,:

Viini laseissa ilkkuen päilyy,
meitä kutsuen kuohuillaan.
:,: Pois murheemme tahdomme karkoittaa.
Äly pois mitä maksoikaan! :,:

Ja kun Integer vitae meille
kerran viimeisen lauletaan.
:,: Silloin ikuisen teekkarin haudalle
oluttynnöri nostetaan. :,:""" }


MATCH_TEXT = {'fi': "<b>Oikein:</b> ",
              'en': "<b>Correct:</b> "}

INVALID_COMMAND = {'fi': "Virheellinen komento.",
                   'en': "Invalid command."}

NOT_ADMIN = {'fi': "Ei ylläpito-oikeuksia!",
             'en': "No admin privileges!"}

FACT_PREFIX = {'fi': "VIIKON ",
               'en': "WEEK "}
FACT_SUFFIX = {'fi': " TEEKKARIFAKTA\n---\n",
               'en': " TEEKKARI FACT\n---\n"}

FACT_NOT_FOUND = {'fi': "Tälle viikolle ei ole faktaa. :(",
                  'en': "No fact for this week. :("}

UNSUPPORTED_FILE_FORMAT = {'fi': "Tiedostotyyppiä ei tueta. :(",
                           'en': "File format not supported. :("}

ALREADY_USER = {'fi': "Olet jo käyttäjä ja saat tiedotteet.",
                'en': "You're already a user and will receive announcements."}

NOT_USER = {'fi': "Et ole käyttäjä, etkä saa tiedotteita. Käytä komentoa /start tilataksesi tiedotteet.",
            'en': "You're not a user, and will not receive announcements. Use command /start to receive announcements."}

USER_DELETED = {'fi': "Käyttäjäsi on poistettu, et saa enää tiedotteita. Voit jatkaa tilausta komennolla /start.",
                'en': "Your user has been removed, and you will no longer receive announcements. You can continue "
                      "receiving announcements with the command /start."}

SPAM = {'fi': "Voit lähettää lörökontsaa enintään kerran 10 minuutissa.",
        'en': "You can only send lörs content a maximum of once per 10 minutes."}

WHICH_SONG = {'fi': "Mikä laulu?",
                 'en': "Which song?"}

SONG_SELECTED = {'fi': " valittu. Lähetä seuraavaksi laulun sanat toistamatta kertosäkeitä.",
                 'en': " selected. Now send the lyrics without repeating choruses."}

PSEUDONYMS = ('Aku Ankka', 'Mikki Hiiri', 'Kolmioukko', 'Nablalover69', 'Teemu Teekkari', 'Fuge', 'Myyrä')

FACT_COMMAND = {'fi': "fakta",
                'en': "fact"}

SONG_COMMAND = {'fi': "laulu",
                'en': "song"}

PREVIOUS_COMMAND = {'fi': 'aiemmat',
                    'en': 'previous'}
