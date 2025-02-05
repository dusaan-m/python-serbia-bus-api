from dataclasses import dataclass


class BaseCityConfig:
    name: str
    url: str
    api_key: str
    stations_endpoint: str
    api_endpoint: str


@dataclass
class AES:
    key: bytes
    iv: bytes


@dataclass(frozen=True, slots=True)
class BeogradConfigBase(BaseCityConfig):
    name = "Beograd"  #: Obicno ime
    url = "https://announcement-bgnaplata.ticketing.rs"
    api_key = "1688dc355af72ef09287"
    stations_endpoint = "/publicapi/v1/networkextended.php"
    api_endpoint = "/publicapi/v2/api.php"

    # AES encryption keys and ivs
    aes_arrivals = AES(
        key=b"3+Lhz8XaOli6bHIoYPGuq9Y8SZxEjX6eN7AFPZuLCLs=",
        iv=b"IvUScqUudyxBTBU9ZCyjow==",
    )
    aes_route = AES(
        key=b"LLUdzKaaLqm2QAyVryeBlAbUaX/1uDJxZAmgPZ2N2r8=",
        iv=b"6GWe4+QzF6NDLS9kRef76A==",
    )
    aes_route_version = AES(
        key=b"0cQXGKcGHSVEcTOt+1UDBzZ5XpzKB+Juz4C6OEnoVwo=",
        iv=b"VsuUn8cH9GWaZshcoWOjbw==",
    )
    aes_line_number = AES(
        key=b"hOKZ6e2ZmzjDWjagmhhmTWme94ao31AlHQ+msJnDS4Q=",
        iv=b"YW62pldkwSXGqoWcclKPeA==",
    )


@dataclass(frozen=True, slots=True)
class NoviSadConfigBase(BaseCityConfig):
    name = "Novi_Sad"
    url = "https://online.nsmart.rs"
    api_key = "4670f468049bbee2260"
    stations_endpoint = "/publicapi/v1/networkextended.php"
    api_endpoint = "/publicapi/v1/announcement/announcement.php"


@dataclass(frozen=True, slots=True)
class NisConfigBase(BaseCityConfig):
    name = "Nis"
    url = "https://online.jgpnis.rs"
    api_key = "1688dc355af72ef09287"
    stations_endpoint = "/publicapi/v1/networkextended.php"
    api_endpoint = "/publicapi/v1/announcement/announcement.php"
