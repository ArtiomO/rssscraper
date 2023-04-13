import pytest
from app.clients.decorators import retry
from app.clients.http import HttpClientConnectionError


class DummyHttpClient:
    """Dummy http client."""

    def __init__(self, status: int, text: str):
        self.response = (status, text)

    @retry(HttpClientConnectionError)
    async def request(self, url: str, method: str) -> (int, str):
        return self.response


class ExceptionHttpClient:
    """Exception http client."""

    @retry(HttpClientConnectionError)
    async def request(self, url: str, method: str) -> (int, str):
        raise HttpClientConnectionError


@pytest.fixture()
def mock_exception_http_client(mocker):
    """Mock exception http client."""

    def factory(module):
        client_instance = ExceptionHttpClient()
        mocker.patch(module, client_instance)

    return factory


@pytest.fixture()
def mock_http_client(mocker):
    """Mock http client."""

    def factory(status: int, result: str, module):
        client_instance = DummyHttpClient(status=status, text=result)
        mocker.patch(module, client_instance)

    return factory


@pytest.fixture()
def rrs_response() -> str:
    rss_response_test = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"
xmlns:atom="http://www.w3.org/2005/Atom"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:media="http://search.yahoo.com/mrss/">
<channel>
<title>NU - Algemeen</title>
<link>https://www.nu.nl/algemeen</link>
<description>Het laatste nieuws het eerst op NU.nl</description>
<atom:link href="https://www.nu.nl/rss/Algemeen" rel="self"></atom:link>
<language>nl-nl</language>
<copyright>Copyright (c) 2023, NU</copyright>
<lastBuildDate>Wed, 05 Apr 2023 17:24:25 +0200</lastBuildDate>
<ttl>60</ttl>
<atom:logo>https://www.nu.nl/algemeenstatic/img/atoms/images/logos/rss-logo-250x40.png</atom:logo>
<item>
<title>Beroemde gorilla Bokito op 27-jarige leeftijd overleden in Diergaarde Blijdorp</title>
<link>https://www.nu.nl/binnenland/6258300/beroemde-gorilla-bokito-op-27-jarige-leeftijd-overleden-in-diergaarde-blijdorp.html</link>
<description>De beroemde gorilla Bokito is dinsdag onverwacht overleden, meldt Diergaarde Blijdorp. Zijn gezondheid was de afgelopen dagen snel achteruitgegaan.</description>
<pubDate>Wed, 05 Apr 2023 16:34:31 +0200</pubDate>
<guid isPermaLink="false">https://www.nu.nl/-/6258300/</guid>
<enclosure length="0" type="image/jpeg" url="https://media.nu.nl/m/6zlxtcsa4xfa_sqr256.jpg/beroemde-gorilla-bokito-op-27-jarige-leeftijd-overleden-in-diergaarde-blijdorp.jpg"></enclosure>
<category>Algemeen</category>
<category>Binnenland</category>
<dc:creator>onze nieuwsredactie</dc:creator>
<dc:rights>copyright photo: Diergaarde Blijdorp</dc:rights>
<atom:link href="https://nu.nl/dieren/6183602/bekijk-beelden-van-de-tiende-nakomeling-van-bokito-in-blijdorp.html" rel="related" title="Bekijk beelden van de tiende nakomeling van Bokito in Blijdorp" type="text/html"></atom:link>
<atom:link href="https://nu.nl/dieren/6183583/blijdorpse-gorilla-bokito-onverwachts-voor-tiende-keer-vader-geworden.html" rel="related" title="Blijdorpse gorilla Bokito onverwachts voor tiende keer vader geworden" type="text/html"></atom:link>
</item>
<item>
<title>Coalitiegenoten D66 en CDA op ramkoers vanwege stikstofdeadline</title>
<link>https://www.nu.nl/provinciale-statenverkiezingen/6258305/coalitiegenoten-d66-en-cda-op-ramkoers-vanwege-stikstofdeadline.html</link>
<description>Coalitiepartijen D66 en CDA worden het niet eens over de stikstofplannen van het kabinet. Laatstgenoemde partij wil opnieuw onderhandelen over de deadline voor halvering van de stikstofuitstoot. D66 ziet dat niet zitten.</description>
<pubDate>Wed, 05 Apr 2023 17:19:13 +0200</pubDate>
<guid isPermaLink="false">https://www.nu.nl/-/6258305/</guid>
<enclosure length="0" type="image/jpeg" url="https://media.nu.nl/m/n87x9vda9n98_sqr256.jpg/coalitiegenoten-d66-en-cda-op-ramkoers-vanwege-stikstofdeadline.jpg"></enclosure>
<category>Algemeen</category>
<category>Politiek</category>
<category>Provinciale Statenverkiezingen</category>
<dc:creator>Edo van der Goot</dc:creator>
<dc:rights>copyright photo: ANP</dc:rights>
</item>
<item>
<title>Spakenburg wil fans confronteren met homofobe spreekkoren, PSV is woest</title>
<link>https://www.nu.nl/voetbal/6258303/spakenburg-wil-fans-confronteren-met-homofobe-spreekkoren-psv-is-woest.html</link>
<description>Spakenburg is van plan om de eigen supporters te confronteren met hun gedrag tijdens het verloren bekerduel met PSV. Xavi Simons was dinsdag het mikpunt van homofobe spreekkoren. PSV heeft een boze brief naar de KNVB gestuurd.</description>
<pubDate>Wed, 05 Apr 2023 17:24:25 +0200</pubDate>
<guid isPermaLink="false">https://www.nu.nl/-/6258303/</guid>
<enclosure length="0" type="image/jpeg" url="https://media.nu.nl/m/vjpx09qayshv_sqr256.jpg/spakenburg-wil-fans-confronteren-met-homofobe-spreekkoren-psv-is-woest.jpg"></enclosure>
<category>Algemeen</category>
<category>Sport</category>
<category>Voetbal</category>
<dc:creator>onze sportredactie</dc:creator>
<dc:rights>copyright photo: Pro Shots</dc:rights>
<atom:link href="https://nu.nl/voetbal/6258220/bekersprookje-spakenburg-eindigt-tegen-psv-dit-kan-ik-ooit-als-opa-vertellen.html" rel="related" title="Bekersprookje Spakenburg eindigt tegen PSV: 'Dit kan ik ooit als opa vertellen'" type="text/html"></atom:link>
<atom:link href="https://nu.nl/nu-voetbal/6258221/bekeravond-in-spakenburg-boze-bellers-mediacircus-en-een-feesttractor.html" rel="related" title="Bekeravond in Spakenburg: boze bellers, mediacircus en een feesttractor" type="text/html"></atom:link>
<atom:link href="https://nu.nl/voetbal/6258217/spakenburg-speler-gaat-zijn-wereldgoal-tegen-psv-nog-heel-vaak-terugkijken.html" rel="related" title="Spakenburg-speler gaat zijn wereldgoal tegen PSV nog heel vaak terugkijken" type="text/html"></atom:link>
<atom:link href="https://nu.nl/voetbal/6258199/de-mooiste-fotos-van-de-historische-bekeravond-in-spakenburg.html" rel="related" title="De mooiste foto's van de historische bekeravond in Spakenburg" type="text/html"></atom:link>
</item>
</channel>
</rss>"""

    return rss_response_test
