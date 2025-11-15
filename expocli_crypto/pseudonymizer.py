"""
Pseudonymization module for French names, addresses, and dates.
Uses Faker library to generate realistic French data.
"""

from faker import Faker
from datetime import datetime, timedelta
import random
import hashlib
from typing import Optional


class Pseudonymizer:
    """Handles pseudonymization of personal data."""

    def __init__(self, locale: str = "fr_FR", seed: Optional[int] = None):
        """
        Initialize pseudonymizer.

        Args:
            locale: Faker locale (default: fr_FR for French)
            seed: Random seed for reproducibility
        """
        self.faker = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def pseudonymize_name(self, original_name: str) -> str:
        """
        Generate a pseudonymized French name.

        Args:
            original_name: Original name

        Returns:
            Pseudonymized French name
        """
        if not original_name or not original_name.strip():
            return original_name

        # Use hash of original to ensure same input -> same output
        name_hash = int(hashlib.sha256(original_name.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(name_hash)

        # Determine if it looks like a full name or just first/last
        parts = original_name.strip().split()

        if len(parts) == 1:
            # Single name - could be first or last
            return temp_faker.last_name()
        elif len(parts) == 2:
            # Likely first + last name
            return f"{temp_faker.first_name()} {temp_faker.last_name()}"
        else:
            # Multiple parts - generate full name
            return temp_faker.name()

    def pseudonymize_address(self, original_address: str) -> str:
        """
        Generate a pseudonymized French address.

        Args:
            original_address: Original address

        Returns:
            Pseudonymized French address
        """
        if not original_address or not original_address.strip():
            return original_address

        # Use hash for deterministic output
        addr_hash = int(hashlib.sha256(original_address.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(addr_hash)

        return temp_faker.address().replace('\n', ', ')

    def pseudonymize_street(self, original_street: str) -> str:
        """Generate a pseudonymized street address."""
        if not original_street or not original_street.strip():
            return original_street

        street_hash = int(hashlib.sha256(original_street.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(street_hash)

        return temp_faker.street_address()

    def pseudonymize_city(self, original_city: str) -> str:
        """Generate a pseudonymized city name."""
        if not original_city or not original_city.strip():
            return original_city

        city_hash = int(hashlib.sha256(original_city.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(city_hash)

        return temp_faker.city()

    def pseudonymize_postal_code(self, original_code: str) -> str:
        """Generate a pseudonymized postal code."""
        if not original_code or not original_code.strip():
            return original_code

        code_hash = int(hashlib.sha256(original_code.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(code_hash)

        return temp_faker.postcode()

    def pseudonymize_date(self, original_date: str, variance_days: int = 30) -> str:
        """
        Pseudonymize a date while preserving age range.

        Args:
            original_date: Original date in YYYY-MM-DD or DD/MM/YYYY format
            variance_days: +/- days to vary the date

        Returns:
            Pseudonymized date in same format as input
        """
        if not original_date or not original_date.strip():
            return original_date

        # Detect format
        date_format = None
        date_obj = None

        # Try different date formats
        formats_to_try = [
            '%Y-%m-%d',  # ISO format
            '%d/%m/%Y',  # French format
            '%Y%m%d',    # Compact format
            '%d-%m-%Y',  # Alternative format
        ]

        for fmt in formats_to_try:
            try:
                date_obj = datetime.strptime(original_date.strip(), fmt)
                date_format = fmt
                break
            except ValueError:
                continue

        if date_obj is None:
            # Could not parse date, return as-is
            return original_date

        # Use hash for deterministic variance
        date_hash = int(hashlib.sha256(original_date.encode()).hexdigest(), 16)
        random.seed(date_hash)

        # Apply random variance within range
        days_offset = random.randint(-variance_days, variance_days)
        new_date = date_obj + timedelta(days=days_offset)

        return new_date.strftime(date_format)

    def pseudonymize_phone(self, original_phone: str) -> str:
        """Generate a pseudonymized French phone number."""
        if not original_phone or not original_phone.strip():
            return original_phone

        phone_hash = int(hashlib.sha256(original_phone.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(phone_hash)

        return temp_faker.phone_number()

    def pseudonymize_email(self, original_email: str) -> str:
        """Generate a pseudonymized email address."""
        if not original_email or not original_email.strip():
            return original_email

        email_hash = int(hashlib.sha256(original_email.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(email_hash)

        return temp_faker.email()

    def pseudonymize_company(self, original_company: str) -> str:
        """Generate a pseudonymized company name."""
        if not original_company or not original_company.strip():
            return original_company

        company_hash = int(hashlib.sha256(original_company.encode()).hexdigest(), 16)
        temp_faker = Faker('fr_FR')
        temp_faker.seed_instance(company_hash)

        return temp_faker.company()
