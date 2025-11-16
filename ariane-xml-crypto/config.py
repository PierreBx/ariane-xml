"""
Configuration management for the encryption module.
"""

import yaml
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
import re


@dataclass
class AttributeRule:
    """Represents an encryption rule for specific attributes."""
    pattern: str  # e.g., "30.001" or "30.001-30.010"
    encryption_type: str  # "fpe", "faker_name", "faker_address", "date_pseudo"
    faker_locale: str = "fr_FR"
    date_variance_days: int = 30  # For date pseudonymization

    def matches(self, attribute: str) -> bool:
        """
        Check if an attribute code matches this rule.
        Attribute format: S10.G00.30.001
        Pattern format: 30.001 or 30.001-30.010
        """
        if not isinstance(attribute, str):
            return False

        # Extract the last two segments (e.g., "30.001" from "S10.G00.30.001")
        match = re.search(r'\.(\d+\.\d+)$', attribute)
        if not match:
            return False

        attr_code = match.group(1)

        # Check if pattern is a range
        pattern_str = str(self.pattern)  # Ensure pattern is string
        if '-' in pattern_str:
            start, end = self.pattern.split('-')
            start_parts = start.split('.')
            end_parts = end.split('.')
            attr_parts = attr_code.split('.')

            if len(start_parts) != 2 or len(end_parts) != 2 or len(attr_parts) != 2:
                return False

            # Check if the first part matches
            if attr_parts[0] != start_parts[0]:
                return False

            # Check if the second part is in range
            try:
                attr_num = int(attr_parts[1])
                start_num = int(start_parts[1])
                end_num = int(end_parts[1])
                return start_num <= attr_num <= end_num
            except ValueError:
                return False
        else:
            # Exact match
            return attr_code == self.pattern


@dataclass
class EncryptionConfig:
    """Main configuration for the encryption module."""

    # Attribute encryption rules
    rules: List[AttributeRule] = field(default_factory=list)

    # FPE settings
    fpe_key: str = ""  # Will be derived from password
    fpe_tweak: str = "ariane-xml"

    # Faker settings
    faker_locale: str = "fr_FR"
    faker_seed: int = None  # For reproducibility if needed

    # Date pseudonymization
    date_variance_days: int = 30  # +/- days to vary dates

    # Mapping table settings
    mapping_table_path: str = "encryption_mapping.json.enc"

    # XML processing
    preserve_structure: bool = True

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'EncryptionConfig':
        """Load configuration from YAML file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        config = cls()

        # Parse attribute rules
        if 'attributes' in data:
            for attr_config in data['attributes']:
                rule = AttributeRule(
                    pattern=attr_config['pattern'],
                    encryption_type=attr_config['type'],
                    faker_locale=attr_config.get('faker_locale', 'fr_FR'),
                    date_variance_days=attr_config.get('date_variance_days', 30)
                )
                config.rules.append(rule)

        # FPE settings
        if 'fpe' in data:
            config.fpe_tweak = data['fpe'].get('tweak', 'ariane-xml')

        # Faker settings
        if 'faker' in data:
            config.faker_locale = data['faker'].get('locale', 'fr_FR')
            config.faker_seed = data['faker'].get('seed')

        # Date settings
        if 'date_pseudonymization' in data:
            config.date_variance_days = data['date_pseudonymization'].get('variance_days', 30)

        # Mapping table
        if 'mapping_table' in data:
            config.mapping_table_path = data['mapping_table'].get('path', 'encryption_mapping.json.enc')

        return config

    def get_rule_for_attribute(self, attribute: str) -> AttributeRule:
        """Get the encryption rule for a specific attribute."""
        for rule in self.rules:
            if rule.matches(attribute):
                return rule
        return None

    def should_encrypt(self, attribute: str) -> bool:
        """Check if an attribute should be encrypted."""
        return self.get_rule_for_attribute(attribute) is not None
