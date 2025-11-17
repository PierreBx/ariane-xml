#ifndef DSN_PARSER_H
#define DSN_PARSER_H

#include "dsn_schema.h"
#include <string>
#include <memory>

namespace ariane_xml {

/**
 * Parser for DSN XSD schemas (P25, P26, etc.)
 * Extracts DSN attribute information and builds the schema model
 */
class DsnParser {
public:
    /**
     * Parse a DSN XSD schema file and return the schema model
     * @param xsdPath Path to the XSD file
     * @param version DSN version (P25, P26, etc.)
     * @return Shared pointer to the parsed schema
     */
    static std::shared_ptr<DsnSchema> parse(const std::string& xsdPath, const std::string& version);

    /**
     * Parse multiple XSD files from a directory (for versions with multiple files)
     * @param schemaDir Path to the schema directory
     * @param version DSN version (P25, P26, etc.)
     * @return Shared pointer to the parsed schema
     */
    static std::shared_ptr<DsnSchema> parseDirectory(const std::string& schemaDir, const std::string& version);

    /**
     * Auto-detect DSN version from an XML file
     * @param xmlPath Path to the XML file
     * @return Detected version (P25, P26, etc.) or empty string if not detected
     */
    static std::string detectVersion(const std::string& xmlPath);

private:
    /**
     * Extract short ID (YY_ZZZ) from full attribute name
     * Example: S21_G00_30_001 -> 30_001
     */
    static std::string extractShortId(const std::string& full_name);

    /**
     * Extract bloc name from attribute name
     * Example: S21_G00_30_001 -> S21.G00.30
     */
    static std::string extractBlocName(const std::string& full_name);

    /**
     * Parse element documentation to extract description
     */
    static std::string extractDescription(const std::string& documentation);

    /**
     * Parse an XSD element and extract DSN attributes
     */
    static void parseElement(void* element, DsnSchema& schema);

    /**
     * Recursively parse complex types
     */
    static void parseComplexType(void* complexType, DsnSchema& schema);
};

} // namespace ariane_xml

#endif // DSN_PARSER_H
