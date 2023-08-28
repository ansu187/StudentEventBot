from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler

import UserDatabase

keywords_dict_fi = {
    "aalef": "Ylioppilaskunnan omistama yritys, joka pyörittää kioskia ja kahta ravintolaa Lappeenrannan kampuksella.",
    "aether": "Lahden kampuksen kilta, joka yhdistää kaikki Lahden LUTin kansainväliset opiskelijat. Kiltaa kutsutaan myös nimellä “eetteri” ja heidät tunnistaa tummankeltaisista haalareista.",
    "alive": "Ylioppilaskunnan verkkomedia, jossa kerrotaan LUTin opiskelijoista ja elämästä kampuksella.",
    "armatuuri": "Energiatekniikan kilta, tunnistaa valkoisista haalareista.",
    "cluster": "Tietotekniikan kilta, tunnistaa punaisista haalareista.",
    "ruusu": "powi.fi/ruusu/",
    "edari": "Edustajisto, ylioppilaskunnan ylin päättävin elin, joka valitaan vaaleilla kahden vuoden välein.",
    "eksursio": "Puhekielessä kursio, useinmiten bussilla tehtävä retki, joka sisältää yleensä yritysvierailun tai pari.",
    "excu": "Puhekielessä kursio, useinmiten bussilla tehtävä retki, joka sisältää yleensä yritysvierailun tai pari.",
    "elut": "Opiskelijoiden verkkopalvelu, joka kokoaa samaan osoitteeseen opiskeluun liittyvät tiedot, tukipalvelut ja kaiken muun tarpeellisen tiedon.",
    "enklaavi": "Kauppatieteiden kilta, tunnistaa neonkeltaisista haalareista.",
    "esn": "Erasmus Student Network (ESN), voittoa tavoittelematon opiskelijajärjestö, joka edustaa kansainvälisiä opiskelijoita. Tavoitteena on vahvistaa kulttuurien välistä ymmärrystä ja opiskelijoina auttaa toinen toistamme. ESN järjestää tapahtumia toistaiseksi vain Lappeenrannassa.",
    "fuksi": "Ensimmäisen vuoden opiskelija.",
    "fuksiläystäke": "Paperilappunen, johon kerätään ensimmäisen vuoden aikana fuksipisteitä suorittamalla erinäisiä tehtäviä tai osallistumalla tapahtumiin.",
    "fuksiviikot": "Uusien opiskelijoiden yliopistotaival alkaa orientaatioviikolla, jota seuraa vielä toinen tapahtumarikas viikko. Näistä kahdesta viikosta puhutaan fuksiviikoista.",
    "g": "Viralliselta nimeltään Cafe Bar G, ylioppilastalon takana sijaitseva kahvila/baari Lappeenrannassa.",
    "g-bar": "Viralliselta nimeltään Cafe Bar G, ylioppilastalon takana sijaitseva kahvila/baari Lappeenrannassa.",
    "cafe bar g": "Viralliselta nimeltään Cafe Bar G, ylioppilastalon takana sijaitseva kahvila/baari Lappeenrannassa.",
    "galleria-aula": "Lappeenrannan kampuksella, kirjaston vieressä sijaitseva aula/luku-/ryhmätyötila, jossa on myös flyygeli.",
    "galleria-noste": "Tila Lappeenrannan Street Cafen ja TEK Loungen välissä, jossa pidetään mm. taidenäyttelyitä.",
    "ruoka": "https://skinfo.dy.fi/",
    "shotgun": "@shotguntapahtuma",
    "hallopedi": "Halloped eli hallinnon opiskelija edustaja, valvoo opiskelijoiden etua esimerkiksi akateemisissa neuvostoissa.",
    "halloped": "Halloped eli hallinnon opiskelija edustaja, valvoo opiskelijoiden etua esimerkiksi akateemisissa neuvostoissa.",
    "hops": "Henkilökohtainen opintosuunnitelma, jonka tarkoitus on helpottaa omien opintojen suunnittelua ja niiden seuraamista.",
    "hässi": "lappeen Rannan opiskelijoiden tekemä wappulehti.",
    "kaplaaki": "Tuotantotalouden kilta, tunnistaa tummansinisistä haalareista.",
    "ketek": "Kemiantekniikan kilta, tunnistaa mustista haalareista.",
    "kellari": "Lappeenrannassa, ylioppilastalon pohjakerroksessa sijaitseva tila, jossa opiskelijat ja järjestöt voivat järjestää juhlia. Kellarissa on myös sauna. Koko tila ja sauna ovat myös opiskelijoiden vuokrattavissa ylioppilaskunnan kautta.",
    "kiltis": "Kiltahuone. Paikka, jossa voit rentoutua opiskelijaystäviesi kesken. Jokaisella ainejärjestöllä on oma kiltahuoneensa ja Lahdessa on järjestöjen yhteinen “kiltahuone”.",
    "kiltakummi": "Killan yhteyshenkilö ylioppilaskunnan hallituksessa.",
    "krk": "Konetekniikan kilta, tunnistaa oransseista haalareista.",
    "kylteri": "Vanhempi kauppatieteenharjoittaja. Fukseista tulee Wappuna Kyltereitä kasteen yhteydessä.",
    "kyykkä": "Perinteinen karjalainen laji, jota LUT-yhteisössä pelataan ahkerasti.",
    "labra": "Skinnarilan suosituin pyöräkellari.",
    "laho": "Lahden opiskelijajärjestöt, tuttavallisemmin LAHO, koostuu kaikista Lahden korkeakoulukampuksen opiskelijayhdistyksistä. Laho-tapahtumat ovat kaikille avoimia.",
    "lappeen ranta": "LUTin opiskelijayhteisössä Lappeenrannasta käytetään usein kirjoitusasua 'lappeen Ranta'.",
    "lateksii": "Laskennallisen tekniikan kilta, tunnistaa fuksianpunaisista haalareista (vanhoilla opiskelijoilla valkoiset haalarit fuksianpunaisin hihoin).",
    "ltky": "Tuttavallisemmin Lytky, eli LUT-yliopiston ylioppilaskunta. Ajaa kaikkien yliopisto-opiskelijoiden asiaa haalarien väriin katsomatta. Ylioppilaskunnan toimisto sijaitsee Ylioppilastalon ensimmäisessä kerroksessa (Lappeenranta) ja M19-kampuksen A-siiven ensimmäisessä kerroksessa (Lahti).",
    "lutikka": "Kulunvalvonta-avain, jolla pääsee koulun tiloihin yön pimeinä tunteina.",
    "monari": "Monitoimisali Lappeenrannan kampuksen 3-vaiheessa eli aivan perällä alimmassa kerroksessa.",
    "moodle": "LUTin opetuksessa ja opiskelussa käytettävä verkko-oppimisalusta. Moodle-oppimisympäristöä käytetään useissa LUTin opintojaksoissa osana opetusta.",
    "n-fuksi": "N-fuksiksi tulee kutsuman LUTin kuudennen vuosikurssin teekkarina tahi kylterinä tunnettua opiskelijaa.",
    "opintopiste": "Opintopisteitä eli noppia olisi tarkoitus keräillä, jotta saavuttaisit diplomi-insinöörin tai kauppatieteiden maisterin tittelin. Opintopisteistä puhutaan myös “noppina”.",
    "noppa": "Opintopisteitä eli noppia olisi tarkoitus keräillä, jotta saavuttaisit diplomi-insinöörin tai kauppatieteiden maisterin tittelin. Opintopisteistä puhutaan myös “noppina”.",
    "orientaatioviikko": "Orientaatioviikko on uusille opiskelijoille olennainen osa opintojen aloittamista. Orientaatioviikko on lukukauden alkamista edeltävä viikko. Orientaatioviikon aikana hoidetaan kurssi-ilmoittautumiset ohjatusti sekä suunnitellaan alkavan lukuvuoden opintoja omien opintojen ohjaajien sekä opintoneuvojien johdolla. Tunnetaan myös nimellä fuksiviikko.",
    "pelletti": "Ympäristötekniikan kilta, tunnistaa harmaista haalareista.",
    "pruju": "Luentomoniste, jonka voit ostaa Aalefin kioskista Lappeenrannassa. Suurin osa nykyisin digimuodossa.",
    "rantasauna": "Myös Skinnarila-saunana tunnettu LUTin rantamökki saunoineen Saimaan rannalla kampuksen läheisyydessä.",
    "saunis": "Saunailta tiistaisin LOAS PK5:n eli Punkkerikatu 5:n saunatiloissa.",
    "sillis": "Silliaamiainen, vuosijuhlien loivennukseen. Usein myös teema (esim. Army, 80’s, Eläintarha, jne…).",
    "sisu": "Opiskelijan käyttöliittymä tentteihin ja opintojaksoille ilmoittautumiseen, yhteystietojen muuttamiseen ja omien suoritustietojen seuraamiseen. Lisäksi Sisussa tehdään opiskelijan henkilökohtainen opintosuunnitelma eli HOPS.",
    "sitsit": "Akateeminen pöytäjuhla, jossa syödään, juodaan ja lauletaan. Fuksit tutustutetaan sitsietikettiin fuksisitseillä.",
    "skinnarilan vapaa valtio": "Lappeenrannan kampuksen ympäristön alueet, jossa kaikki käyttäytyvät Skinnarilan hengen mukaisesti.",
    "svv": "Skinnarilan Vapaa Valtio - Lappeenrannan kampuksen ympäristön alueet, jossa kaikki käyttäytyvät Skinnarilan hengen mukaisesti.",
    "ekonomit": "Kauppatieteellisen yliopistotutkinnon suorittaneiden ja alan opiskelijoiden palvelu- ja etujärjestö.",
    "sätky": "Sähkötekniikan kilta, tunnistaa vihreistä haalareista.",
    "tapahtuma-areena": "Lahden kampuksen aulatila, jossa voi hengailla, järjestää tapahtumia, pelata ja nauttia kahvilan tarjonnasta.",
    "teekkari": "Vanhempi tekniikan opiskelija. Fukseista tulee Wappuna Teekkareita kasteen yhteydessä.",
    "tek": "Tekniikan akateemiset, tekniikan opiskelijoiden ja diplomi-insinöörien ammattijärjestö.",
    "tupsufuksi": "Henkilö, jolla on teekkarilakki käytössään ensimmäistä vuotta. Yleensä siis toisen vuoden opiskelija.",
    "tupsu": "Henkilö, jolla on teekkarilakki käytössään ensimmäistä vuotta. Yleensä siis toisen vuoden opiskelija.",
    "tuutori": "Auttajasi, ohjaajasi, neuvojasi ja ystäväsi koko opintotaipaleesi ajan.",
    "yolo": "Ylioppilastalon ravintola.",
    "vierula": "LOAS:n rantamökki saunoineen Saimaan rannalla Skinnarilankadun varrella.",
    "vuosijuhlat": "Eli vujut, killan tai järjestön synttärit, sisältää yleensä upeat akateemiset pöytäjuhlat, eli tosi hienot sitsit.",
    "vujut": "Eli vujut, killan tai järjestön synttärit, sisältää yleensä upeat akateemiset pöytäjuhlat, eli tosi hienot sitsit.",
    "wappu": "Koko vuoden huipennus, jota Lappeenrannassa juhlitaan muuta Suomea pidemmän kaavan mukaan. Vuonna 2023 Wappua juhlittiin 36 päivää.",
    "vappu": "Tarkoititko Wappu?\n\nKoko vuoden huipennus, jota Lappeenrannassa juhlitaan muuta Suomea pidemmän kaavan mukaan. Vuonna 2023 Wappua juhlittiin 36 päivää.",
    "häirintä": "LTKY:n häirintäyhdyshenkilö on Niilo Hendolin: niilo.hendolin@ltky.fi 044 293 8820",
    "härö": "LTKY:n häirintäyhdyshenkilö on Niilo Hendolin: niilo.hendolin@ltky.fi 044 293 8820",
    "häirintäyhdyshenkilö": "LTKY:n häirintäyhdyshenkilö on Niilo Hendolin: niilo.hendolin@ltky.fi 044 293 8820",
    "häirintä yhdys henkilö": "LTKY:n häirintäyhdyshenkilö on Niilo Hendolin: niilo.hendolin@ltky.fi 044 293 8820",
    "kafi": "Grilliseuran asuntovaunu yliopistonkadun varrella. Täytti 18 vuonna 2023"

    }

keywords_dict_en = {
    "aalef": "A company owned by the Student Union. It runs a kiosk and two restaurants in Lappeenranta campus.",
    "aether": "Student association for all the international programs at the LUT Lahti campus, identified by dark yellow overalls.",
    "alive": "The online media of the Student Union, with colorful stories and articles about LUT students and life on campus.",
    "armatuuri": "Energy technology guild, white overalls.",
    "cluster": "Information technology guild, red overalls.",
    "credit": "Credits should be collected in order to achieve the title of Master of Science (MSc) or Master of Business Administration. Credits are also referred to as “noppa.”",
    "excursion": "A trip made usually by bus, may include business visits and other nice activities.",
    "elut": "An online student service that gathers study-related information, support services, and all other necessary information at the same site.",
    "enklaavi": "Student association of Business students, neon yellow overalls.",
    "esn": "Erasmus Student Network (ESN), a non-profit student organization that represents international students. The goal is to strengthen intercultural understanding and as students help each other. For now, ESN only organizes events in Lappeenranta.",
    "event arena": "A lobby space at Lahti campus, where you can hang out, hold events, play games and enjoy the café products.",
    "freshman": "Also called Fresher, is a first year student.",
    "freshman point card": "Or fresher slip, is a paper on which freshmen collect points in their first year by completing various tasks and participating in events.",
    "freshman weeks": "The university path for new students begins with an orientation week, followed by another eventful week. These two weeks are called freshman weeks.",
    "g": "Officially Cafe Bar G, a student-friendly café / restaurant next to the Student Union building in Lappeenranta.",
    "gallery lounge": "At the Lappeenranta campus, next to the library, there is a lobby/reading/group work space that also has a grand piano.",
    "gallery neste": "Space between Street Cafe and TEK Lounge, where art exhibitions are held in Lappeenranta.",
    "guild": "An independent association of students from a particular degree program that organizes events and advocacy for its members.",
    "guild sponsor": "Guild contact person from the Student Union board.",
    "guild room": "A place where you can relax at the campus with student friends. Each guild has its own guild room and in Lahti there is one common room for all associations.",
    "halloped": "HallOpEd is an administrative student representative, who oversees students’ interests in, for example, academic councils.",
    "hops": "Or PSP is the personal study plan.",
    "hässi": "Student magazine from “lappeen Ranta” published by the organization Powi ry during April.",
    "kaplaaki": "Production economy guild, dark blue overalls.",
    "ketek": "Chemical engineering guild, black overalls.",
    "kellari": "A cellar located at the ground floor of the Student Union building in Lappeenranta. Students and guilds can organize events and enjoy the sauna there, the place can be rented through the Student Union websites.",
    "krk": "Mechanical engineering guild, orange overalls.",
    "kylteri": "Senior business student. Freshmen become Kylteris during the baptism in Wappu.",
    "kyykkä": "Traditional karelian sport, which is highly played at the LUT community.",
    "labra": "Skinnarila’s most popular bicycle cellar.",
    "laho": "Lahti student associations, more commonly known as Laho, consists of all the student associations at the campus. Laho events are open for everyone.",
    "lappeen ranta": "Often, the student community likes to write “Lappeenranta” in a humorous way.",
    "lateksii": "Computational technology guild, fuchsia pink overalls.",
    "ltky": "Or “Lytky,” the Student Union of LUT University. Pursues the interests of all students in the university regardless of the color of the overalls. The student union office is located at the ground floor of the student union building (Lappeenranta) and on the ground floor of A-wing M19-campus (Lahti).",
    "lutikka": "An access control key that allows access to the campus doors at any time in Lappeenranta.",
    "monari": "A multi-purpose hall on the ground floor of the 3rd phase of the Lappeenranta campus.",
    "moodle": "An online learning platform for teaching and learning. The Moodle learning environment is used in several LUT courses as part of the teaching.",
    "n-fresher": "“N-freshmen will be called any LUT student who is known to be a sixth-year teekkari or kylteri.”",
    "orientation week": "Orientation week is an essential part of starting studies for new students. The orientation week is the week before the start of the semester. During the orientation week, course registrations are handled under supervision and studies for the beginning of the academic year are planned under the guidance of the supervisors and study advisors. Also known as freshman week.",
    "pelletti": "Environmental technology guild, gray overalls.",
    "pruju": "Lecture handout, which can be purchased from the Aalef Kiosk in LUT main building in Lappeenranta. Most of them are digital nowadays.",
    "repco": "The representative council is the highest decision-making body of the Student Union, elected every two years.",
    "saunis": "A free sauna evening held on Tuesdays at the sauna space of LOAS PK5, which is Punkkerikatu 5.",
    "shotgun": "@shotguntapahtuma",
    "sillis": "A casual breakfast event after an annual ball. Usually with a theme (e.g. Army, 80’s, Zoo, etc…).",
    "sisu": "Student interface for registering for exams and courses, changing contact information and tracking your own performance information.",
    "fresher sitz": "An academic table party where you eat, drink and sing according to etiquette. Freshmen are introduced to etiquette during Freshman Sitz.",
    "fresher sits": "An academic table party where you eat, drink and sing according to etiquette. Freshmen are introduced to etiquette during Freshman Sitz.",
    "skinnarila sauna": "LUT’s cottage with saunas on the shores of Lake Saimaa near the campus.",
    "svv": "Areas around the Lappeenranta campus where everyone behaves in the spirit of Skinnarila.",
    "ekonomit": "Finnish Economic Association for business students and graduates.",
    "sätky": "Electrical engineering guild, green overalls.",
    "tassel fresher": "Tupsufuksi, a person who is wearing its Teekkari cap for the first year. Usually it’s a sophomore.",
    "tek": "Tekniikan Akateemiset or association of Academic engineers and architects in Finland.",
    "tutor": "Your helper, mentor, advisor and friend throughout your studies.",
    "vierula": "LOAS’s cottage with saunas on the shores of Lake Saimaa along Skinnarilankatu.",
    "vujut": "Annual ball, guild or association birthday, or a great academic celebration. It usually includes a gorgeous academic table party, or fancy sitz.",
    "wappu": "Nationally Vappu is May Day (1st of May) celebration. In the student community, Wappu is the culmination of the whole year, which is celebrated in Lappeenranta according to a longer formula than the rest of Finland. In 2023, Wappu was celebrated for 36 days."

    }

async def BasicHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_input = user_input.lower()



    user_input = user_input.lower()  # Convert user input to lowercase

    if UserDatabase.get_user_lang_code(update) == 0:
        if user_input in keywords_dict_fi:
            await update.message.reply_text(keywords_dict_fi[user_input])



    elif UserDatabase.get_user_lang_code(update) == 1:
        if user_input in keywords_dict_en:
            await update.message.reply_text(keywords_dict_en[user_input])









