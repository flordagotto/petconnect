from dataclasses import dataclass


@dataclass(frozen=True)
class MerchantData:
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    user_id: int
    refresh_token: str
    public_key: str

    def as_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "scope": self.scope,
            "user_id": self.user_id,
            "refresh_token": self.refresh_token,
            "public_key": self.public_key,
        }

    @staticmethod
    def from_dict(data: dict) -> "MerchantData":
        return MerchantData(
            access_token=data["access_token"],
            token_type=data["token_type"],
            expires_in=data["expires_in"],
            scope=data["scope"],
            user_id=data["user_id"],
            refresh_token=data["refresh_token"],
            public_key=data["public_key"],
        )
