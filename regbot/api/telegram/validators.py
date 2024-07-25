import re


class PhoneNumberValidator:
    def __call__(self, raw_value: str) -> float:
        if re.match(
            r"^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$",
            raw_value,
        ):
            return raw_value
        else:
            raise ValueError("Номер введен неправильно")
