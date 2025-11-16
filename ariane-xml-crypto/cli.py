#!/usr/bin/env python3
"""
Command-line interface for Ariane-XML encryption module.
"""

import argparse
import sys
import getpass
from pathlib import Path
import json

from .config import EncryptionConfig
from .encryptor import XMLEncryptor
from .mapping_table import MappingTable


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Ariane-XML XML Encryption Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encrypt an XML file
  ariane-xml-encrypt encrypt input.xml output.xml -c config.yaml

  # Decrypt an XML file
  ariane-xml-encrypt decrypt encrypted.xml decrypted.xml -c config.yaml

  # Export mapping table to plaintext JSON
  ariane-xml-encrypt export-mapping -c config.yaml -o mapping.json

  # Show mapping statistics
  ariane-xml-encrypt stats -c config.yaml
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt an XML file')
    encrypt_parser.add_argument('input', help='Input XML file')
    encrypt_parser.add_argument('output', help='Output encrypted XML file')
    encrypt_parser.add_argument('-c', '--config', required=True, help='YAML configuration file')
    encrypt_parser.add_argument('-p', '--password', help='Encryption password (will prompt if not provided)')
    encrypt_parser.add_argument('--mapping', help='Path to mapping table (overrides config)')
    encrypt_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt an XML file')
    decrypt_parser.add_argument('input', help='Input encrypted XML file')
    decrypt_parser.add_argument('output', help='Output decrypted XML file')
    decrypt_parser.add_argument('-c', '--config', required=True, help='YAML configuration file')
    decrypt_parser.add_argument('-p', '--password', help='Decryption password (will prompt if not provided)')
    decrypt_parser.add_argument('--mapping', help='Path to mapping table (overrides config)')
    decrypt_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Export mapping command
    export_parser = subparsers.add_parser('export-mapping', help='Export mapping table to plaintext JSON')
    export_parser.add_argument('-c', '--config', required=True, help='YAML configuration file')
    export_parser.add_argument('-p', '--password', help='Mapping table password (will prompt if not provided)')
    export_parser.add_argument('-o', '--output', required=True, help='Output JSON file')
    export_parser.add_argument('--mapping', help='Path to mapping table (overrides config)')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show mapping table statistics')
    stats_parser.add_argument('-c', '--config', required=True, help='YAML configuration file')
    stats_parser.add_argument('-p', '--password', help='Mapping table password (will prompt if not provided)')
    stats_parser.add_argument('--mapping', help='Path to mapping table (overrides config)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get password if not provided
    if hasattr(args, 'password'):
        password = args.password
        if not password:
            password = getpass.getpass('Enter encryption password: ')
    else:
        password = None

    try:
        if args.command == 'encrypt':
            encrypt_command(args, password)
        elif args.command == 'decrypt':
            decrypt_command(args, password)
        elif args.command == 'export-mapping':
            export_mapping_command(args, password)
        elif args.command == 'stats':
            stats_command(args, password)
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def encrypt_command(args, password):
    """Execute encrypt command."""
    print(f"Loading configuration from {args.config}...")
    config = EncryptionConfig.from_yaml(args.config)

    if args.mapping:
        config.mapping_table_path = args.mapping

    print(f"Encrypting {args.input} -> {args.output}...")
    encryptor = XMLEncryptor(config, password)
    stats = encryptor.encrypt_file(args.input, args.output)

    print("\nEncryption completed successfully!")
    print(f"Total attributes: {stats['total_attributes']}")
    print(f"Encrypted attributes: {stats['encrypted_attributes']}")

    if stats['by_type']:
        print("\nBy encryption type:")
        for enc_type, count in stats['by_type'].items():
            print(f"  {enc_type}: {count}")

    print(f"\nMapping table saved to: {config.mapping_table_path}")

    if args.verbose:
        mapping_stats = encryptor.mapping_table.get_statistics()
        print("\nMapping table statistics:")
        for category, count in mapping_stats.items():
            print(f"  {category}: {count} entries")


def decrypt_command(args, password):
    """Execute decrypt command."""
    print(f"Loading configuration from {args.config}...")
    config = EncryptionConfig.from_yaml(args.config)

    if args.mapping:
        config.mapping_table_path = args.mapping

    # Check if mapping table exists
    if not Path(config.mapping_table_path).exists():
        print(f"Error: Mapping table not found at {config.mapping_table_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Decrypting {args.input} -> {args.output}...")
    encryptor = XMLEncryptor(config, password)
    stats = encryptor.decrypt_file(args.input, args.output)

    print("\nDecryption completed successfully!")
    print(f"Total attributes: {stats['total_attributes']}")
    print(f"Decrypted attributes: {stats['encrypted_attributes']}")


def export_mapping_command(args, password):
    """Execute export-mapping command."""
    config = EncryptionConfig.from_yaml(args.config)

    if args.mapping:
        config.mapping_table_path = args.mapping

    # Check if mapping table exists
    if not Path(config.mapping_table_path).exists():
        print(f"Error: Mapping table not found at {config.mapping_table_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading mapping table from {config.mapping_table_path}...")
    mapping = MappingTable(password, config.mapping_table_path)

    print(f"Exporting to {args.output}...")
    mapping.export_plaintext(args.output)

    print(f"\nMapping table exported successfully to {args.output}")
    stats = mapping.get_statistics()
    print(f"Total categories: {len(stats)}")
    for category, count in stats.items():
        print(f"  {category}: {count} entries")


def stats_command(args, password):
    """Execute stats command."""
    config = EncryptionConfig.from_yaml(args.config)

    if args.mapping:
        config.mapping_table_path = args.mapping

    # Check if mapping table exists
    if not Path(config.mapping_table_path).exists():
        print(f"Error: Mapping table not found at {config.mapping_table_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading mapping table from {config.mapping_table_path}...")
    mapping = MappingTable(password, config.mapping_table_path)

    stats = mapping.get_statistics()
    print("\nMapping Table Statistics")
    print("=" * 50)
    print(f"Total categories: {len(stats)}")
    print(f"Total entries: {sum(stats.values())}")
    print("\nBy category:")
    for category, count in sorted(stats.items()):
        print(f"  {category}: {count} entries")


if __name__ == '__main__':
    main()
